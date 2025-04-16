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
from string import Template
from typing import List, Optional

from kag.interface import PromptABC
from knext.schema.client import SchemaClient


@PromptABC.register("MedReports_ner")
class OpenIENERPrompt(PromptABC):

    template_zh = """
    {
        "instruction": "You are an expert in Named Entity Recognition. Extract entities that match the schema definition from the input. If no entity of that type exists, return an empty list. Respond in JSON string format. You can refer to the example for extraction.",
        "schema": $schema,
        "example": [
            {
                "input": "The cardiomediastinal silhouette and pulmonary vasculature are within normal limits. There is no pneumothorax or pleural effusion. There are no focal areas of consolidation. Cholecystectomy clips are present. Small T-spine osteophytes. There is biapical pleural thickening, unchanged from prior. Mildly hyperexpanded lungs.",
                "output": [
                        {"entity": "cardiomediastinal silhouette", "category": "CardiacSilhouette"},
                        {"entity": "pulmonary vasculature", "category": "PulmonaryVasculature"},
                        {"entity": "pneumothorax", "category": "Pneumothorax"},
                        {"entity": "pleural effusion", "category": "PleuralEffusion"},
                        {"entity": "focal areas of consolidation", "category": "Consolidation"},
                        {"entity": "Cholecystectomy clips", "category": "SurgicalClips"},
                        {"entity": "T-spine osteophytes", "category": "Osteophyte"},
                        {"entity": "biapical pleural thickening", "category": "Thickening"},
                        {"entity": "hyperexpanded lungs", "category": "Hyperinflation"}
                    ]
            }
        ],
        "input": "$input"
    }    
        """

    template_en = template_zh

    def __init__(self, language: Optional[str] = "en", **kwargs):
        super().__init__(language, **kwargs)
        self.schema = SchemaClient(project_id=self.project_id).extract_types()
        self.template = Template(self.template).safe_substitute(schema=self.schema)

    @property
    def template_variables(self) -> List[str]:
        return ["input"]

    def parse_response(self, response: str, **kwargs):
        rsp = response
        if isinstance(rsp, str):
            rsp = json.loads(rsp)
        if isinstance(rsp, dict) and "output" in rsp:
            rsp = rsp["output"]
        if isinstance(rsp, dict) and "named_entities" in rsp:
            entities = rsp["named_entities"]
        else:
            entities = rsp

        return entities
