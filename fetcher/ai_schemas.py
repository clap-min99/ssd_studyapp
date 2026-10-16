"""Structured output contracts for OpenAI Responses API."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ArticleOutput(BaseModel):
    title: str
    links: list[str] = Field(default_factory=list)
    summary: str = ""
    insight: str = ""
    category: Literal["ssd", "automotive"]
    tags: list[str] = Field(default_factory=list)
    source_text: str = ""


class LearningOutput(BaseModel):
    heading: str
    body: str = ""
    tags: list[str] = Field(default_factory=list)
    source_text: str = ""


class TermOutput(BaseModel):
    term: str
    meaning: str = ""
    relevance: str = ""


class DigestOutput(BaseModel):
    date: Optional[str] = None
    articles: list[ArticleOutput] = Field(default_factory=list)
    learning_items: list[LearningOutput] = Field(default_factory=list)
    terms: list[TermOutput] = Field(default_factory=list)
    no_article_categories: list[Literal["ssd", "automotive"]] = Field(default_factory=list)


class AnswerOutput(BaseModel):
    verdict: Literal["correct", "partial", "wrong"]
    feedback: str


class CardSummaryOutput(BaseModel):
    summary: str


class TagsOutput(BaseModel):
    tags: list[str]


class SourcesOutput(BaseModel):
    sources: list[str]
