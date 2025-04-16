# -*- coding: utf-8 -*-
# Copyright 2023 OpenSPG Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

import json
from typing import Optional, List


from kag.interface import PromptABC


@PromptABC.register("MedReports_std")
class OpenIEEntitystandardizationdPrompt(PromptABC):
    template_zh = """
{
    "instruction": "The 'input' field contains context provided by the user. The 'named_entities' field contains named entities extracted from the context, which might be ambiguous abbreviations, aliases, or slang. To disambiguate, try to provide the official names for these entities based on the context and your own knowledge. Note that entities with the same meaning should have only one official name. Please respond in a single JSONArray string format, following the format of the 'output' field in the provided example, without any explanation.",
    "example": {
        "input": "The CMS and pulm vasc are WNL. No PTX or effusion. No focal consolidation. Chole clips present. Small T-spine osteophytes. Biapical pleural thickening, stable. Mildly hyperinflated lungs.",
        "named_entities": [
            {"entity": "CMS", "category": "CardiacSilhouette"},
            {"entity": "pulm vasc", "category": "PulmonaryVasculature"},
            {"entity": "PTX", "category": "Pneumothorax"},
            {"entity": "effusion", "category": "PleuralEffusion"},
            {"entity": "focal consolidation", "category": "Consolidation"},
            {"entity": "Chole clips", "category": "SurgicalClips"},
            {"entity": "T-spine osteophytes", "category": "Osteophyte"},
            {"entity": "biapical pleural thickening", "category": "Thickening"},
            {"entity": "hyperinflated lungs", "category": "Hyperinflation"}
        ],
        "output": [
            {"entity": "CMS", "category": "CardiacSilhouette", "official_name": "Cardiomediastinal Silhouette"},
            {"entity": "pulm vasc", "category": "PulmonaryVasculature", "official_name": "Pulmonary Vasculature"},
            {"entity": "PTX", "category": "Pneumothorax", "official_name": "Pneumothorax"},
            {"entity": "effusion", "category": "PleuralEffusion", "official_name": "Pleural Effusion"},
            {"entity": "focal consolidation", "category": "Consolidation", "official_name": "Focal Consolidation"},
            {"entity": "Chole clips", "category": "SurgicalClips", "official_name": "Cholecystectomy Clips"},
            {"entity": "T-spine osteophytes", "category": "Osteophyte", "official_name": "Thoracic Spine Osteophytes"},
            {"entity": "biapical pleural thickening", "category": "Thickening", "official_name": "Biapical Pleural Thickening"},
            {"entity": "hyperinflated lungs", "category": "Hyperinflation", "official_name": "Lung Hyperinflation"}
        ]
    },
    "input": $input,
    "named_entities": $named_entities,
}    
    """

    template_en = template_zh

    @property
    def template_variables(self) -> List[str]:
        return ["input", "named_entities"]

    def parse_response(self, response: str, **kwargs):
        rsp = response
        if isinstance(rsp, str):
            rsp = json.loads(rsp)
        if isinstance(rsp, dict) and "output" in rsp:
            rsp = rsp["output"]
        if isinstance(rsp, dict) and "named_entities" in rsp:
            standardized_entity = rsp["named_entities"]
        else:
            standardized_entity = rsp
        entities_with_offical_name = set()
        merged = []
        entities = kwargs.get("named_entities", [])
        for entity in standardized_entity:
            merged.append(entity)
            entities_with_offical_name.add(entity["entity"])
        # in case llm ignores some entities
        for entity in entities:
            if entity["entity"] not in entities_with_offical_name:
                entity["official_name"] = entity["entity"]
                merged.append(entity)
        return merged
