source .env
#Docker
sudo apt update -y
sudo apt install -y docker
sudo service docker start
sudo usermod -a -G docker ubuntu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

#Frontend: React - NVM/NPM
cd frontend || return
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
nvm install node
npm i
sudo chown -R ubuntu /home/ubuntu/Adatest/Adatest-App/frontend/.next

#Backend: Python - Django
cd ../backend || return
pip install --upgrade pip
pip install notebook==6.1.5
pip install -r mistral_requirements.txt
huggingface-cli login --token ${HUGGINGFACE_TOKEN} --add-to-git-credential

