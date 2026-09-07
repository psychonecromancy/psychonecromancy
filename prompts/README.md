# prompts/

Versioned system prompts used by AI Agent nodes in the n8n workflows (e.g.
the prompt that turns a society/period string into a ComfyUI image
generation prompt).

Name files by what they're for and version them explicitly if a prompt
changes in a way worth tracking (e.g. `image-prompt-v1.md`,
`image-prompt-v2.md`) rather than overwriting silently, since prompt
changes materially affect output quality and it's useful to know what
prompt produced a given sample in `samples/`.
