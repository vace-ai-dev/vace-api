# VACE API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/kling/kling-motion-control?utm_source=github&utm_medium=ugc&utm_campaign=vace-ai-dev&utm_content=readme-badge&utm_term=tier-a)

VACE is Alibaba's all-in-one video creation and editing framework: one model that handles reference-to-video, video-to-video, masked inpainting and outpainting, and any combination of those in a single pass. This package is a Python client that gives you a VACE API for the two most common jobs, driving a character image with a reference video and animating a still image from a prompt, with `pip install vace-api` and no local GPU.

You get a blocking `run()` that returns when the video is ready, a submit-and-poll path for queued jobs, webhook delivery for servers that must not block, and a single runtime dependency (`requests`). It is built for backend services, content pipelines and notebooks that want controllable video generation as a function call.

> **Try it now:** [https://synexa.ai/explore/kling/kling-motion-control](https://synexa.ai/explore/kling/kling-motion-control?utm_source=github&utm_medium=ugc&utm_campaign=vace-ai-dev&utm_content=readme-top&utm_term=tier-a) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About VACE](#about-vace)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **The 14B checkpoint is not a laptop model.** Wan2.1-VACE-14B at 720p needs a data-centre class GPU, and the 1.3B model only reaches 480p. The hosted endpoints run on hardware sized for the job.
- **No pipeline assembly.** Self-hosting VACE means installing Wan 2.1, the VACE preprocessors for depth, pose, flow and masks, and the annotator models behind them. The hosted endpoint takes an image and a video and returns a video.
- **No cold start.** Loading a 14B diffusion transformer plus its text encoder and VAE onto a GPU takes minutes before the first frame; a hosted run starts on a warm model.
- **Per-run pricing.** `kling/kling-motion-control` is $0.112 per run and `tongyi/wan2.2` image-to-video is $0.20 per 5 second clip. You pay for completed runs, not for idle instances.

## Installation

```bash
pip install git+https://github.com/vace-ai-dev/vace-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=vace-ai-dev&utm_content=readme-apikey&utm_term=tier-a)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import vace_api

output = vace_api.run({
    "reference_image": "https://example.com/input.png",
    "reference_video": "https://example.com/input.png"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from vace_api import Client

client = Client(api_key="sk-...")
output = client.run({"reference_image": "https://example.com/input.png", "reference_video": "https://example.com/input.png"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`kling/kling-motion-control`](https://synexa.ai/explore/kling/kling-motion-control?utm_source=github&utm_medium=ugc&utm_campaign=vace-ai-dev&utm_content=readme-models&utm_term=tier-a) | image-to-video | Kling 3.0 motion control: transfer motion from a reference video to any character image with improved consistency and quality. | $0.112 |
| [`tongyi/wan2.2`](https://synexa.ai/explore/tongyi/wan2.2?utm_source=github&utm_medium=ugc&utm_campaign=vace-ai-dev&utm_content=readme-models&utm_term=tier-a) | image-to-video | Generate 5s 480p videos using Wan 2.2 14B. A comprehensive video foundation models that pushes the boundaries of video generation. | $0.2 |

The default model is **`kling/kling-motion-control`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `kling/kling-motion-control`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | no | — | — | Optional text prompt to guide motion, elements, and background (max 2500 chars) |
| `reference_image` | file | yes | — | — | Reference character image (.jpg/.jpeg/.png, max 10MB, 340-3850px, aspect 1:2.5 to 2.5:1) |
| `reference_video` | file | yes | — | — | Reference performance video (.mp4/.mov, max 100MB, 3-10s) |
| `keep_original_sound` | boolean | no | `True` | — | Keep the original audio from the reference video |

### `tongyi/wan2.2`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `A woman is talking` | — | Input prompt |
| `input_image` | file | yes | `https://files.synexa.ai/models/wan-image…` | — | Input image to start generating from |
| `aspect_ratio` | string | no | `9:16` | 9:16, 1:1, 16:9 | Video Resolution |
| `seed` | integer | no | `random` | — | Random seed. Leave blank to randomize the seed |
| `num_frames` | integer | no | `81` | 1, 81 | Video Frames |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from vace_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About VACE

VACE (*All-in-One Video Creation and Editing*) was published by Alibaba's Tongyi Lab in March 2025 and accepted at ICCV 2025. Its contribution is a unified interface for conditional video generation: instead of training a separate model for each task, it introduces the Video Condition Unit, a single input structure that packs text, reference images or videos, and spatiotemporal masks, and a Context Adapter that injects those conditions into a frozen video diffusion transformer. The public checkpoints are Wan2.1-VACE-1.3B and Wan2.1-VACE-14B, with an earlier LTX-Video preview.

Because conditions are composable, one model covers reference-to-video (keep a subject or style from an image), video-to-video (repaint a clip guided by depth, pose, optical flow, scribbles or grayscale), masked video-to-video (inpaint or outpaint a region across time) and combinations of these. The project groups them as Move-Anything, Swap-Anything, Reference-Anything, Expand-Anything and Animate-Anything. The 14B model generates at 480p and 720p; the 1.3B model at 480p.

Outputs are short clips, typically 81 frames at 16 fps, and the usual diffusion-video caveats apply: identity can drift on long or fast motion, small text and hands are unreliable, and the preprocessing step (pose extraction, depth estimation) has to be run separately before the model sees the video.

The hosted endpoint used by this client is `kling/kling-motion-control`, which provides the same reference-to-video capability (a reference character image plus a reference video produces a new video with that motion); the original VACE weights are available at https://github.com/ali-vilab/VACE if you want to self-host. For plain image-to-video from a prompt, the client also exposes `tongyi/wan2.2`, the 14B Wan 2.2 model from the same Alibaba lab that VACE is built on.

**Official project:** https://github.com/ali-vilab/VACE

## Use cases

- **Character motion transfer** — pass a character image as `reference_image` and a 3 to 10 second acted clip as `reference_video` to `run()` and receive the character performing that motion.
- **Product image to video** — call the `tongyi/wan2.2` endpoint with a packshot as `input_image` and a prompt describing the camera move to get a 5 second clip.
- **Dance and choreography templates** — keep one reference performance and swap `reference_image` per creator to generate many versions of the same routine.
- **Storyboard previsualisation** — animate each concept frame with a short prompt to check pacing before committing to a full shoot.
- **Bulk social clips** — iterate over a spreadsheet of images and prompts, submit jobs without blocking, and collect results with a webhook.
- **Sound-preserving remixes** — set `keep_original_sound=True` so the generated video keeps the reference clip's audio track for lip-synced or music-driven content.

## FAQ

**Is there a VACE API?**

Not from Alibaba directly; VACE ships as model weights and a PyTorch repository. This package wraps hosted Synexa endpoints that provide the same reference-to-video and image-to-video capabilities, so you can call them over HTTPS without running the model.

**How much does the VACE API cost?**

The default endpoint, `kling/kling-motion-control`, is $0.112 per run. The `tongyi/wan2.2` image-to-video endpoint is $0.20 per run for a 5 second 480p clip. Billing is per completed run.

**Can I run VACE without a GPU?**

Not locally; even the 1.3B model needs a CUDA GPU, and the 14B model needs a large one. With this client the generation happens on the hosted side, so any machine that can make an HTTPS request will do.

**Does this client work with the original ali-vilab VACE repo, Wan 2.1 or ComfyUI?**

No. It does not load local weights, run the VACE preprocessors, or talk to the ComfyUI WanVideo VACE nodes. It is an HTTP client for the hosted endpoints only.

**What input formats does it accept?**

For `kling/kling-motion-control`: `reference_image` is .jpg, .jpeg or .png up to 10 MB, 340 to 3850 px per side, aspect ratio between 1:2.5 and 2.5:1; `reference_video` is .mp4 or .mov up to 100 MB and 3 to 10 seconds. Both are required. For `tongyi/wan2.2` you pass a `prompt` and an `input_image`, with optional `aspect_ratio`, `num_frames` and `seed`.

**Is this the official VACE SDK?**

No. This is an independent client and is not affiliated with Alibaba or Tongyi Lab. The official project is at https://github.com/ali-vilab/VACE.

## Related

- [VACE (official repository)](https://github.com/ali-vilab/VACE)
- [Synexa Python client](https://github.com/synexa-ai/synexa-python)
- [kling/kling-motion-control on Synexa](https://synexa.ai/explore/kling/kling-motion-control)
- [tongyi/wan2.2 on Synexa](https://synexa.ai/explore/tongyi/wan2.2)

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of VACE. Model weights and trademarks belong to their respective owners.



_Last reviewed: 2026-09-22_
