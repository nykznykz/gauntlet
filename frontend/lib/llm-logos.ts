// Mapping of LLM providers to their logo images
export const LLM_LOGOS: Record<string, string> = {
  anthropic: '/logos/claude_logo.png',
  openai: '/logos/openai_logo.png',
  azure: '/logos/openai_logo.png', // Azure OpenAI uses OpenAI logo
  deepseek: '/logos/deepseek_logo.png',
  qwen: '/logos/qwen_logo.png', // Add Qwen logo when available
};

/**
 * Get the logo path for a given LLM provider
 * @param provider - The LLM provider name (anthropic, openai, azure, deepseek, qwen)
 * @returns The path to the logo image or null if not found
 */
export function getLLMLogo(provider: string): string | null {
  const normalizedProvider = provider.toLowerCase();
  return LLM_LOGOS[normalizedProvider] || null;
}

/**
 * Extract the LLM provider from a participant name
 * Common patterns: "Claude-Sonnet", "GPT-4-Turbo", "DeepSeek-V3", etc.
 * @param participantName - The participant name
 * @returns The LLM provider name or null if not recognized
 */
export function extractProviderFromName(participantName: string): string | null {
  const name = participantName.toLowerCase();

  if (name.includes('claude') || name.includes('sonnet') || name.includes('opus') || name.includes('haiku')) {
    return 'anthropic';
  }
  if (name.includes('gpt') || name.includes('openai')) {
    return 'openai';
  }
  if (name.includes('deepseek')) {
    return 'deepseek';
  }
  if (name.includes('qwen')) {
    return 'qwen';
  }
  if (name.includes('azure')) {
    return 'azure';
  }

  return null;
}

/**
 * Get the logo for a participant by name
 * @param participantName - The participant name
 * @returns The path to the logo image or null if not found
 */
export function getParticipantLogo(participantName: string): string | null {
  const provider = extractProviderFromName(participantName);
  return provider ? getLLMLogo(provider) : null;
}
