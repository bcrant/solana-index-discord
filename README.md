# Solana Index Discord
An index of Solana DeFi Tokens measured in units of SOL. 

Receive updates directly from your Discord Server by installing the bot and running `/sol` command.

## Set Up
`* Clone repo *`   
`$ mkdir sol-idx`  
`$ cd sol-idx`  

### Node
`$ nvm install --lts`  
`$ nvm use --lts`  
`$ node -v > .nvmrc`  

`* Set up AWS CLI profile *`

### AWS CDK
`$ npm install aws-cdk-lib`  
`$ npm install -g aws-cdk`  

`cdk bootstrap aws://{AWS_ACCOUNT_NUMBER}/{AWS_REGION}`  
`cdk init app --language typescript`  
 
`git init`    

### Python
`pyenv install 3.9.5`  
`pyenv virtualenv 3.9.5 solana_index`  
`pyenv local solana_index`  
`pip install --upgrade pip`  
`pip install -r ./sol-idx/lambda-layer/requirements.txt`  