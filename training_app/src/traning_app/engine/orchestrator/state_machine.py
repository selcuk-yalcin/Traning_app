"""Orchestrator stages: idle → planning → research → generating → layout → done | failed."""

from enum import Enum


class JobStage(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    RESEARCH = "research"
    GENERATING = "generating"
    LAYOUT = "layout"
    TTS = "tts"
    RENDER = "render"
    DONE = "done"
    FAILED = "failed"
