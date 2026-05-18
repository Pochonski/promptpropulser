"""
PromptPropulserClaude — FastAPI Server

Endpoints:
  POST /optimize    — optimize a prompt (returns optimized prompt)
  POST /generate    — optimize + send to Claude + return response
  POST /ab          — A/B test raw vs PPC
  GET  /health      — health check
  GET  /modes       — list available modes
  GET  /sessions    — list saved sessions
"""

import os
import sys
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ppc.schemas.input import InputSchema, InputOptions
from ppc.engine.pipeline import run_pipeline
from ppc.integration.anthropic import AnthropicClient
from ppc.loop import run_once
from ppc.config.modes import MODE_MATRIX
from ppc.session_store import load_logs, DEFAULT_SESSIONS_DIR


app = FastAPI(
    title="PromptPropulserClaude API",
    version="1.0.0",
    description="Contextual cognition orchestration layer for LLMs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OptimizeRequest(BaseModel):
    mode: str = Field(default="basic", pattern="^(basic|reflection|code|architect|brutal|focus|teacher|compress)$")
    prompt: str = Field(..., min_length=1)
    reinforcement_level: str = Field(default="medium", pattern="^(none|low|medium|aggressive|maximum)$")
    reflection_depth: int = Field(default=0, ge=0, le=5)
    compression: bool = False
    token_budget: int = Field(default=4000, ge=100, le=32000)


class GenerateRequest(OptimizeRequest):
    api_key: str = ""
    model: str = "claude-sonnet-4-6"
    system_prompt: str = ""
    max_tokens: int = Field(default=4096, ge=1, le=32000)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class ABRequest(GenerateRequest):
    pass


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/modes")
def list_modes():
    return {
        "modes": [
            {
                "key": mode.key,
                "reflection_depth": mode.reflection_depth,
                "reinforcement": mode.reinforcement,
                "description": mode.key,
            }
            for mode in MODE_MATRIX.values()
        ]
    }


@app.post("/optimize")
def optimize(req: OptimizeRequest):
    try:
        schema = InputSchema(
            mode=req.mode,
            prompt=req.prompt,
            options=InputOptions(
                reinforcement_level=req.reinforcement_level,
                reflection_depth=req.reflection_depth,
                compression=req.compression,
                strict_constraints=True,
                token_budget=req.token_budget,
            ),
        )
        output = run_pipeline(schema)
        return {
            "mode": req.mode,
            "optimized_prompt": output.optimized_prompt,
            "complexity_score": output.analyzed_intent.complexity_score,
            "constraints_locked": output.constraints.locked,
            "constraints_soft": output.constraints.soft,
            "reinforcement_level": output.reinforcement.level,
            "semantic_echoes": len(output.semantic_echoes),
            "token_usage": {
                "input": output.token_usage.input_tokens,
                "optimization": output.token_usage.optimization_tokens,
                "final": output.token_usage.final_prompt_tokens,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        api_key = req.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")

        client = AnthropicClient(api_key=api_key, model=req.model)
        schema = InputSchema(
            mode=req.mode,
            prompt=req.prompt,
            options=InputOptions(
                reinforcement_level=req.reinforcement_level,
                reflection_depth=req.reflection_depth,
                compression=req.compression,
                strict_constraints=True,
                token_budget=req.max_tokens,
            ),
        )
        loop_result = run_once(
            schema, client,
            system_prompt=req.system_prompt or None,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )

        return {
            "mode": req.mode,
            "optimized_prompt": loop_result.session_log.optimized_prompt_v1,
            "llm_response": loop_result.final_response,
            "critic_scores": {
                "constraint_following": loop_result.session_log.critic_score.constraint_following,
                "clarity": loop_result.session_log.critic_score.clarity,
                "accuracy": loop_result.session_log.critic_score.accuracy,
                "efficiency": loop_result.session_log.critic_score.efficiency,
            },
            "critic_issues": loop_result.session_log.detected_failures,
            "passed_critic": loop_result.passed_critic,
            "session_id": loop_result.session_log.session_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ab")
def ab_test(req: ABRequest):
    try:
        api_key = req.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")

        client = AnthropicClient(api_key=api_key, model=req.model)

        raw_response = client.generate(
            prompt=req.prompt,
            system_prompt=req.system_prompt or None,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )

        schema = InputSchema(
            mode=req.mode,
            prompt=req.prompt,
            options=InputOptions(
                reinforcement_level=req.reinforcement_level,
                reflection_depth=req.reflection_depth,
                compression=req.compression,
                strict_constraints=True,
                token_budget=req.max_tokens,
            ),
        )
        loop_result = run_once(
            schema, client,
            system_prompt=req.system_prompt or None,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )

        from ppc.reflection.critic import evaluate_response
        from ppc.schemas.output import DetectedConstraints

        raw_critic = evaluate_response(
            raw_response.text, req.prompt, req.prompt, DetectedConstraints(),
        )

        return {
            "raw": {
                "prompt": req.prompt,
                "response": raw_response.text[:3000],
                "tokens": raw_response.output_tokens,
                "critic": {
                    "constraint_following": raw_critic.score.constraint_following,
                    "clarity": raw_critic.score.clarity,
                    "accuracy": raw_critic.score.accuracy,
                    "efficiency": raw_critic.score.efficiency,
                },
            },
            "ppc": {
                "optimized_prompt": loop_result.session_log.optimized_prompt_v1,
                "response": loop_result.final_response[:3000],
                "tokens": len(loop_result.final_response.split()),
                "critic": {
                    "constraint_following": loop_result.session_log.critic_score.constraint_following,
                    "clarity": loop_result.session_log.critic_score.clarity,
                    "accuracy": loop_result.session_log.critic_score.accuracy,
                    "efficiency": loop_result.session_log.critic_score.efficiency,
                },
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
def list_sessions(limit: int = 20):
    logs = load_logs(DEFAULT_SESSIONS_DIR)
    recent = logs[-limit:]
    return {
        "count": len(recent),
        "total": len(logs),
        "sessions": [
            {
                "session_id": log.session_id,
                "timestamp": log.timestamp,
                "mode": log.mode_used,
                "complexity": log.complexity_at_start,
                "critic_avg": log.critic_score.average(),
                "passed": log.critic_score.constraint_following >= 5,
            }
            for log in recent
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
