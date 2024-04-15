import logging
import random

import torch
import transformers
import torch.nn as nn
from torch.cuda.amp import autocast as autocast
from ETrain.utils.LAVIS.common.registry import registry
from ETrain.Models.InstructBlip.base_model import disabled_train
from ETrain.Models.MiniGPT.minigpt_base import MiniGPTBase
from ETrain.Models.InstructBlip.Qformer import BertConfig, BertLMHeadModel
from transformers.modeling_utils import load_state_dict, get_checkpoint_shard_files, _load_state_dict_into_model
from transformers.deepspeed import is_deepspeed_zero3_enabled
from transformers import LlamaConfig, AutoConfig, AutoModelForCausalLM
from ETrain.Models.InstructBlip.modeling_llama import LlamaForCausalLM

class MiniGPTv2Config(LlamaConfig):
    model_type = "minigpt_v2"

@registry.register_model("minigpt_v2")
class MiniGPTv2(MiniGPTBase):
    """
    MiniGPT-v2 model
    """

    PRETRAINED_MODEL_CONFIG_DICT = {
        "pretrain": "configs/LAVIS/models/minigpt_v2.yaml",
    }
    config_class = MiniGPTv2Config

    # def __init__(
    #         self,
    #         config,  # the device of 8bit model should be set when loading and cannot be changed anymore.
    # ):
    #     super().__init__(
    #         config,
    #     )

    #     img_f_dim = self.visual_encoder.num_features * 4
    #     self.llama_proj = nn.Linear(
    #         img_f_dim, self.llama_model.config.hidden_size
    #     )
    #     self.chat_template = config.chat_template


    def __init__(
            self,
            vit_model="eva_clip_g",
            img_size=448,
            drop_path_rate=0,
            use_grad_checkpoint=False,
            vit_precision="fp16",
            freeze_vit=True,
            llama_model="",
            prompt_template='[INST] {} [/INST]',
            max_txt_len=300,
            end_sym='\n',
            lora_r=64,
            lora_target_modules=["q_proj", "v_proj"],
            lora_alpha=16,
            lora_dropout=0.05,
            chat_template=False,
            use_grad_checkpoint_llm=False,
            max_context_len=3800,
            low_resource=False,  # use 8 bit and put vit in cpu
            device_8bit=0,  # the device of 8bit model should be set when loading and cannot be changed anymore.
    ):
        super().__init__(
            vit_model=vit_model,
            img_size=img_size,
            drop_path_rate=drop_path_rate,
            use_grad_checkpoint=use_grad_checkpoint,
            vit_precision=vit_precision,
            freeze_vit=freeze_vit,
            llama_model=llama_model,
            max_txt_len=max_txt_len,
            max_context_len=max_context_len,
            end_sym=end_sym,
            prompt_template=prompt_template,
            low_resource=low_resource,
            device_8bit=device_8bit,
            lora_r=lora_r,
            lora_target_modules=lora_target_modules,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
        )

        img_f_dim = self.visual_encoder.num_features * 4
        self.llama_proj = nn.Linear(
            img_f_dim, self.llama_model.config.hidden_size
        )
        self.chat_template = chat_template

    def encode_img(self, image):
        device = image.device

        if len(image.shape) > 4:
            image = image.reshape(-1, *image.shape[-3:])

        with self.maybe_autocast():
            image_embeds = self.ln_vision(self.visual_encoder(image))
            image_embeds = image_embeds[:, 1:, :]
            bs, pn, hs = image_embeds.shape
            image_embeds = image_embeds.view(bs, int(pn / 4), int(hs * 4))

            inputs_llama = self.llama_proj(image_embeds)
            atts_llama = torch.ones(inputs_llama.size()[:-1], dtype=torch.long)
        return inputs_llama, atts_llama

    @classmethod
    def from_config(cls, cfg):
        vit_model = cfg.get("vit_model", "eva_clip_g")
        img_size = cfg.get("image_size")
        llama_model_path = cfg.get("llama_model")

        drop_path_rate = cfg.get("drop_path_rate", 0)
        use_grad_checkpoint = cfg.get("use_grad_checkpoint", False)
        vit_precision = cfg.get("vit_precision", "fp16")
        freeze_vit = cfg.get("freeze_vit", True)
        low_resource = cfg.get("low_resource", False)

        prompt_template = cfg.get("prompt_template", '[INST] {} [/INST]')
        max_txt_len = cfg.get("max_txt_len", 300)
        end_sym = cfg.get("end_sym", '\n')

        lora_r = cfg.get("lora_r", 64)
        lora_alpha = cfg.get("lora_alpha", 16)
        chat_template = cfg.get("chat_template", False)

        use_grad_checkpoint_llm = cfg.get("use_grad_checkpoint_llm", False)
        max_context_len = cfg.get("max_context_len", 3800)

        # model = MiniGPTv2(config = config)
        
        model = cls(
            vit_model=vit_model,
            img_size=img_size,
            drop_path_rate=drop_path_rate,
            use_grad_checkpoint=use_grad_checkpoint,
            vit_precision=vit_precision,
            freeze_vit=freeze_vit,
            llama_model=llama_model_path,
            prompt_template=prompt_template,
            max_txt_len=max_txt_len,
            low_resource=low_resource,
            end_sym=end_sym,
            lora_r=lora_r,
            lora_alpha=lora_alpha,
            chat_template=chat_template,
            use_grad_checkpoint_llm=use_grad_checkpoint_llm,
            max_context_len=max_context_len,
        )

        ckpt_path = cfg.get("ckpt", "")  # load weights of MiniGPT-4
        if ckpt_path:
            print("Load Minigpt-4-LLM Checkpoint: {} device: {}".format(ckpt_path, model.device))
            print()
            ckpt = load_state_dict(ckpt_path)
            if is_deepspeed_zero3_enabled():
                msg = _load_state_dict_into_model(model, ckpt['model'],start_prefix = '')
            else:
                msg = model.load_state_dict(ckpt['model'], strict=False)

        return model


AutoConfig.register("minigpt_v2", MiniGPTv2Config)
AutoModelForCausalLM.register(MiniGPTv2Config, MiniGPTv2)