# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
from typing import Dict, List

import torch.cuda
from fairseq.models.bart import BARTModel

from tapex.processor import get_default_processor

logger = logging.getLogger(__name__)


class TAPEXModelInterfaceTabFact:
    """
    A simple model interface to tapex for online prediction
    """

    def __init__(self, resource_dir, checkpoint_name, table_processor=None):
        self.model = BARTModel.from_pretrained(model_name_or_path=resource_dir,
                                               checkpoint_file=checkpoint_name)
        if torch.cuda.is_available():
            self.model.cuda()
        self.model.eval()
        if table_processor is not None:
            self.tab_processor = table_processor
        else:
            self.tab_processor = get_default_processor(max_cell_length=15, max_input_length=1024)

    def predict(self, question: str, table_context: Dict) -> List[str]:
        call_back_label = lambda label: self.model.task.label_dictionary.string(
        [label + self.model.task.label_dictionary.nspecial]
        )
        
        print("Label dictionary:", self.model.task.label_dictionary)
        
        # process input
        model_input = self.tab_processor.process_input(table_context, question, []).lower()
        tokens = self.model.encode(model_input)
        print("Raw forward pass", self.model.predict('sentence_classification_head', tokens).argmax().item())
        pred = call_back_label(self.model.predict('sentence_classification_head', tokens).argmax().item())
        
        print("Prediction:", pred)
        
        return pred