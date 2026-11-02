# Pokémon Legends: Arceus Recomp

Um projeto amador independente focado na recompilação de **Pokémon Legends: Arceus**.

Este projeto é uma experiência de aprendizado pessoal, desenvolvida com o conhecimento, tempo e recursos disponíveis. Estou fazendo o meu melhor para que funcione, aprimorá-lo e compartilhar meu progresso com a comunidade.

Não sou um desenvolvedor profissional e este não é um produto oficial, finalizado ou comercial. Bugs, limitações, problemas de compatibilidade e recursos incompletos são esperados.

## Apoie o Projeto

Se você gosta deste projeto e gostaria de me ajudar a dedicar mais tempo ao desenvolvimento, testes, solução de problemas e melhorias futuras, você pode me apoiar por meio de uma das opções abaixo.

- **Patreon:** Adicione o link da sua página do Patreon aqui.

- **Pix:** `53578c64-d11f-43c5-96b9-3b5529741664`

Toda contribuição é voluntária e apreciada. Obrigado por apoiar este projeto amador!

## Créditos e Isenção de Responsabilidade

Este é um projeto independente e não oficial feito por fãs. Não é afiliado, endossado ou patrocinado pela Nintendo ou Game Freak.

Projetos da comunidade como [LASRecomp](https://github.com/peiikai/LASRecomp) e [PokeZ-ARecomp](https://github.com/Hexveil404/PokeZ-ARecomp) serviram como referência para aprendizado e pesquisa. Os créditos por suas respectivas ferramentas e trabalhos pertencem aos seus autores originais.

Não distribua arquivos de jogos protegidos por direitos autorais, ROMs, recursos extraídos, código proprietário, chaves de criptografia ou outros materiais pertencentes à Nintendo ou Game Freak por meio deste repositório.


## Configurando os Arquivos do Jogo

Para recompilar e executar este projeto, você precisa fornecer os arquivos extraídos da sua própria cópia legal de **Pokémon Legends: Arceus**.

**Os arquivos originais do jogo não estão incluídos nem são distribuídos neste projeto.**

### 1. Extraia os arquivos do jogo

Você precisará extrair o conteúdo de ExeFS e RomFS da sua própria cópia do jogo.

### 2. Coloque os arquivos nas pastas corretas

Dentro do diretório principal do projeto, localize a pasta `extracted`.

Coloque os arquivos extraídos na seguinte estrutura:


Pokemon Arceus Recompzada/
└── extracted/
    ├── exefs/
    │   ├── main
    │   ├── sdk
    │   ├── subsdk0
    │   ├── subsdk1
    │   └── outros arquivos ExeFS necessários
    │
    └── romfs/
        ├── bin/
        ├── system_resource/
        └── outros arquivos extraídos do jogo


**Importante:** Coloque o conteúdo das pastas ExeFS e RomFS dentro de suas respectivas pastas. Não coloque os arquivos compactados nem a pasta principal que contém ambas.

### 3. Recompile o jogo

Depois de configurar os arquivos:

1. Execute `recompilar_arceus.bat` ou `lasrecomp.exe`.
2. Aguarde a conclusão do processo de geração de código e compilação.
3. Quando a compilação terminar, execute `executar_arceus.bat` ou abra `lasrecomp.exe`.

A primeira compilação pode levar algum tempo, dependendo do hardware do seu computador.

### Aviso importante

Cada usuário deve fornecer os arquivos extraídos de sua própria cópia do jogo. Não compartilhe nem distribua arquivos originais pertencentes à Nintendo, Game Freak ou The Pokémon Company.
