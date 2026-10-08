"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt():
    """Dados do prompt v2 (o conteúdo fica sob a chave bug_to_user_story_v2)."""
    return load_prompts(str(PROMPT_FILE))["bug_to_user_story_v2"]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt
        assert prompt["system_prompt"].strip(), "system_prompt está vazio"

    def test_prompt_has_role_definition(self, prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt["system_prompt"]
        assert "Você é" in system_prompt, "O prompt não define uma persona ('Você é ...')"
        assert "Product Manager" in system_prompt

    def test_prompt_mentions_format(self, prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt["system_prompt"]
        assert "Como um" in system_prompt and "eu quero" in system_prompt and "para que" in system_prompt, \
            "O prompt não exige o formato 'Como um ... eu quero ... para que ...'"
        assert "Critérios de Aceitação" in system_prompt

    def test_prompt_has_few_shot_examples(self, prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt["system_prompt"]
        assert system_prompt.count("Relato de Bug:") >= 2, "Menos de 2 exemplos de entrada"
        assert system_prompt.count("User Story:") >= 2, "Menos de 2 exemplos de saída"

    def test_prompt_no_todos(self, prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        text = prompt["system_prompt"] + prompt["user_prompt"]
        assert "[TODO]" not in text
        assert "TODO" not in text

    def test_minimum_techniques(self, prompt):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt.get("techniques_applied", [])
        assert len(techniques) >= 2, f"Mínimo de 2 técnicas, encontradas: {len(techniques)}"

    def test_prompt_structure_is_valid(self, prompt):
        """Valida a estrutura geral com a função auxiliar de utils.py."""
        is_valid, errors = validate_prompt_structure(prompt)
        assert is_valid, f"Estrutura inválida: {errors}"

    def test_user_prompt_has_bug_report_variable(self, prompt):
        """O user_prompt precisa da variável usada no dataset de avaliação."""
        assert "{bug_report}" in prompt["user_prompt"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
