import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { LambdaIntegration, MethodLoggingLevel, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { PolicyStatement } from 'aws-cdk-lib/aws-iam';
import s3 = require('aws-cdk-lib/aws-s3');
import { Construct } from 'constructs';
import path = require('path');
import * as dotenv from 'dotenv';
dotenv.config();

console.log('PROCESS.ENV', process.env);

process.env.DISCORD_APP_NAME
process.env.DISCORD_APP_ID
process.env.DISCORD_PUBLIC_KEY
process.env.DISCORD_SECRET as string,
DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN as string,
DISCORD_BOT_PERMISSIONS: process.env.DISCORD_BOT_PERMISSIONS as string,



interface LambdaApiStackProps extends StackProps {
  functionName: string
}

export class SolIdxStack extends Stack {
  private restApi: RestApi
  private lambdaFunction: Function
  private bucket: s3.Bucket
  
  constructor(scope: Construct, id: string, props: LambdaApiStackProps) {
    super(scope, id, props);

    this.bucket = new s3.Bucket(this, "solana-index-discord-bucket")
    
    const lambdaPolicy = new PolicyStatement()
    lambdaPolicy.addActions("s3:ListBucket")
    lambdaPolicy.addResources(this.bucket.bucketArn)
      
    // this.lambdaFunction = new Function(this, props.functionName, {
    //   functionName: props.functionName,
    //   code: Code.fromAsset(path.join(__dirname, '../lambda')),
    //   runtime: Runtime.PYTHON_3_9,
    //   handler: "index.handler",
    //   timeout: Duration.seconds(20),
    //   memorySize: 512,
    //   environment: {
    //     DISCORD_APP_NAME: process.env.DISCORD_APP_NAME as string,
    //     DISCORD_APP_ID: process.env.DISCORD_APP_ID as string,
    //     DISCORD_PUBLIC_KEY: process.env.DISCORD_PUBLIC_KEY as string,
    //     DISCORD_SECRET: process.env.DISCORD_SECRET as string,
    //     DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN as string,
    //     DISCORD_BOT_PERMISSIONS: process.env.DISCORD_BOT_PERMISSIONS as string,
    //   },
    //   initialPolicy: [lambdaPolicy],
    // });

    this.lambdaFunction = new PythonFunction(this, props.functionName, {
      functionName: props.functionName,
      entry: './lambda',
      runtime: Runtime.PYTHON_3_9,
      timeout: Duration.seconds(20),
      memorySize: 512,
      environment: {
        DISCORD_APP_NAME: process.env.DISCORD_APP_NAME as string,
        DISCORD_APP_ID: process.env.DISCORD_APP_ID as string,
        DISCORD_PUBLIC_KEY: process.env.DISCORD_PUBLIC_KEY as string,
        DISCORD_SECRET: process.env.DISCORD_SECRET as string,
        DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN as string,
        DISCORD_BOT_PERMISSIONS: process.env.DISCORD_BOT_PERMISSIONS as string,
      },
      initialPolicy: [lambdaPolicy],
    })

    const restApiName: string = "solana-index-discord-api"    
    this.restApi = new RestApi(this, restApiName, {
      restApiName: restApiName,
      deployOptions: {
        stageName: "prod",
        metricsEnabled: true,
        loggingLevel: MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
      },
    });

    const discord = this.restApi.root.addResource("discord");
    discord.addMethod("GET", new LambdaIntegration(this.lambdaFunction, {}), {
      apiKeyRequired: true,
    }); 

    const apiKey = this.restApi.addApiKey("api-key", {
      apiKeyName: "solana-index-discord-api-key",
    });

    const usagePlan = this.restApi.addUsagePlan("api-key-usage-plan", {
      name: "solana-index-discord-api-usage-plan",
      throttle: {
        rateLimit: 10,
        burstLimit: 2
      },
    });
  
    usagePlan.addApiKey(apiKey);
    usagePlan.addApiStage({ stage: this.restApi.deploymentStage });
  }
}
