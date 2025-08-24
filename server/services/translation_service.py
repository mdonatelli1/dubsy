import asyncio
from typing import Dict, List

import openai
from config.settings import settings
from utils.exceptions import TranslationError


class TranslationService:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    async def translate_segments(
        self, segments: List[Dict], target_language: str = "fr"
    ) -> List[Dict]:
        """Traduit une liste de segments"""
        if not segments:
            return []

        translated_segments = []

        for i, segment in enumerate(segments):
            try:
                translated_text = await self._translate_single_segment(
                    segment["text"], target_language
                )

                # Créer le segment traduit
                translated_segment = segment.copy()
                translated_segment["text"] = translated_text
                translated_segments.append(translated_segment)

                # Délai pour éviter les rate limits
                if i < len(segments) - 1:  # Pas de délai après le dernier
                    await asyncio.sleep(settings.TRANSLATION_DELAY)

            except Exception as e:
                print(f"Erreur lors de la traduction du segment {i + 1}: {str(e)}")
                # En cas d'erreur, garder le texte original
                translated_segments.append(segment)

        return translated_segments

    async def _translate_single_segment(self, text: str, target_language: str) -> str:
        """Traduit un segment individuel"""
        try:
            response = self.client.chat.completions.create(
                model=settings.TRANSLATION_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate text to {target_language} while preserving meaning, tone, and style. Only return the translation, no additional text.",
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=200,
                temperature=0.1,
            )

            return response.choices[0].message.content.strip()

        except openai.APIError as e:
            raise TranslationError(f"Erreur API OpenAI lors de la traduction: {str(e)}")
        except Exception as e:
            raise TranslationError(f"Erreur lors de la traduction: {str(e)}")
