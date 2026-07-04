# Guia de Configuração de Backups Multi-Nuvem (rclone)

Para garantir a redundância dos seus dados, o AstroTools suporta múltiplos serviços de nuvem através do `rclone`.

## 1. Instalação
Certifique-se de que o `rclone` está instalado:
```bash
sudo apt install rclone
```

## 2. Configuração (Exemplo: Proton Drive / GDrive / OneDrive)
1. Execute o assistente de configuração:
   ```bash
   rclone config
   ```
2. Escolha `n` (New remote).
3. Dê um nome (ex: `astro_backup`).
4. Selecione o serviço (ex: `drive` para Google Drive, `onedrive`, etc.).
5. Siga as instruções no navegador para autenticar.

## 3. Integração com AstroTools
No seu ficheiro `.env` na raiz do projeto, adicione:
```env
RCLONE_REMOTE=astro_backup:astro_data
RCLONE_PATH=/mnt/c/Work/git/astrotools/uploads/gallery
```
A partir de agora, o botão "Sincronizar Agora" no Dashboard utilizará estas definições para enviar os dados para a nuvem.
