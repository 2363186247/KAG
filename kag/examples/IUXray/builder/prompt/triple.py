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


@PromptABC.register("MedReports_triple")
class OpenIETriplePrompt(PromptABC):
    template_zh = """
{
    "instruction": "You are an expert specialized in Open Information Extraction (OpenIE). Please extract any possible relationships (including subject, predicate, object) from the text in the 'input' field and list them in JSON format, following the example format in the 'example' field. Pay attention to the following requirements: 1. Each triple should contain at least one, but preferably two, named entities from the 'entity_list'. 2. Explicitly resolve pronouns to specific names to maintain clarity.",
    "entity_list": $entity_list,
    "input": "$input",
    "example": {
        "input": "The cardiomediastinal silhouette and pulmonary vasculature are within normal limits. There is no pneumothorax or pleural effusion. There are no focal areas of consolidation. Cholecystectomy clips are present. Small T-spine osteophytes. There is biapical pleural thickening, unchanged from prior. Mildly hyperexpanded lungs.",
        "entity_list": [
            {"entity": "cardiomediastinal silhouette", "category": "CardiacSilhouette"},
            {"entity": "pulmonary vasculature", "category": "PulmonaryVasculature"},
            {"entity": "pneumothorax", "category": "Pneumothorax"},
            {"entity": "pleural effusion", "category": "PleuralEffusion"},
            {"entity": "focal areas of consolidation", "category": "Consolidation"},
            {"entity": "Cholecystectomy clips", "category": "SurgicalClips"},
            {"entity": "T-spine osteophytes", "category": "Osteophyte"},
            {"entity": "biapical pleural thickening", "category": "Thickening"},
            {"entity": "lungs", "category": "Lungs"},
            {"entity": "hyperexpanded lungs", "category": "Hyperinflation"}
        ],
        "output":[
            ["cardiomediastinal silhouette", "are", "within normal limits"],
            ["pulmonary vasculature", "are", "within normal limits"],
            ["pneumothorax", "is absent", "no"],
            ["pleural effusion", "is absent", "no"],
            ["focal areas of consolidation", "are absent", "no"],
            ["Cholecystectomy clips", "are", "present"],
            ["T-spine osteophytes", "are", "Small"],
            ["biapical pleural thickening", "is", "present"],
            ["biapical pleural thickening", "is", "unchanged from prior"],
            ["lungs", "are", "Mildly hyperexpanded"]
        ]
    }
}    
    """

    template_en = template_zh

    @property
    def template_variables(self) -> List[str]:
        return ["entity_list", "input"]

    def parse_response(self, response: str, **kwargs):
        rsp = response
        if isinstance(rsp, str):
            rsp = json.loads(rsp)
        if isinstance(rsp, dict) and "output" in rsp:
            rsp = rsp["output"]
        if isinstance(rsp, dict) and "triples" in rsp:
            triples = rsp["triples"]
        else:
            triples = rsp

        standardized_triples = []
        for triple in triples:
            if isinstance(triple, list):
                standardized_triples.append(triple)
            elif isinstance(triple, dict):
                s = triple.get("subject")
                p = triple.get("predicate")
                o = triple.get("object")
                if s and p and o:
                    standardized_triples.append([s, p, o])

        return standardized_triples
