"""Interactive CLI for the OpenAI-powered store assistant."""

import asyncio
import os

from dotenv import load_dotenv

from src.agent.orchestrator import create_agent, respond


async def main() -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Defina OPENAI_API_KEY no ambiente ou no arquivo .env. Consulte .env.example.")

    agent = create_agent()
    history: list = []
    print("Empório da Música 🎵 Olá! Como posso ajudar? (digite 'sair' para encerrar)")
    while True:
        try:
            message = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEmpório: Até mais! Boa música! 🎶")
            break
        if message.casefold() in {"sair", "exit", "quit"}:
            print("Empório: Até mais! Boa música! 🎶")
            break
        if not message:
            continue
        try:
            result = await respond(agent, message, history)
        except Exception as exc:
            print(f"Empório: Não consegui acessar o atendimento agora. Tente novamente em instantes. ({exc.__class__.__name__})")
            continue
        print("Empório:", result.final_output)
        history = result.to_input_list()


if __name__ == "__main__":
    asyncio.run(main())
