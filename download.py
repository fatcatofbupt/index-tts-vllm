from modelscope import snapshot_download
#model_dir = snapshot_download('Qwen/Qwen2.5-14B-Instruct')

model_name="iic/SenseVoiceSmall"
#model_name="fishaudio/fish-speech-1.4"
model_name="Qwen/Qwen2.5-32B-Instruct-AWQ"
#[model_name="Qwen/Qwen2.5-14B-Instruct-AWQ"
model_name="fishaudio/fish-speech-1.5"
model_name="fishaudio/fish-speech-1.5"
model_name="iic/SenseVoiceSmall"
model_name="fishaudio/fish-speech-1.4"
model_name="Qwen/Qwen2.5-32B-Instruct-AWQ"
model_name="pengzhendong/FireRedASR-AED-L"
model_name="iic/speech_frcrn_ans_cirm_16k"
model_name="BadToBest/EchoMimicV2"
model_name="stabilityai/sd-vae-ft-mse"
model_name="gqy2468/sd-image-variations-diffusers"
model_name="Qwen/Qwen3-32B-AWQ"
model_name="fishaudio/openaudio-s1-mini"
model_name="fishaudio/fish-speech-1.4"
model_name="fishaudio/fish-speech-1.5"
model_name="IndexTeam/IndexTTS-1.5"
snapshot_download(model_name)
assert False
