import { Construct } from 'constructs';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { 
  Cors,
  LambdaIntegration, 
  MethodLoggingLevel, 
  RequestValidator,
  RestApi,
} from 'aws-cdk-lib/aws-apigateway';
import { Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { PolicyStatement } from 'aws-cdk-lib/aws-iam';
import s3 = require('aws-cdk-lib/aws-s3');

import path = require('path');
const dotenv = require('dotenv').config({path: path.join('', '../.env')});


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
      defaultCorsPreflightOptions: {
        allowOrigins: Cors.ALL_ORIGINS,
      },
    });

    const restApiValidator = new RequestValidator(this, restApiName + '-validator', {
      restApi: this.restApi,
      validateRequestBody: true,
      validateRequestParameters: true,
    });

    // const discord = this.restApi.root.addResource("discord");
    // discord.addMethod("GET", new LambdaIntegration(this.lambdaFunction, {}), {
    //   apiKeyRequired: true,
    // }); 

    // User authentication endpoint configuration
    const discordBotEventItems = this.restApi.root.addResource("event", {
      defaultCorsPreflightOptions: {
        allowOrigins: [
          "*",
        ],
      },
    });

    // Transform our requests and responses as appropriate.
    const discordBotIntegration: LambdaIntegration = new LambdaIntegration(this.lambdaFunction, {
      proxy: false,
      requestTemplates: {
        'application/json': '{\r\n\
              "timestamp": "$input.params(\'x-signature-timestamp\')",\r\n\
              "signature": "$input.params(\'x-signature-ed25519\')",\r\n\
              "jsonBody" : $input.json(\'$\')\r\n\
            }',
      },
      integrationResponses: [
        {
          statusCode: '200',
        },
        {
          statusCode: '401',
          selectionPattern: '.*[UNAUTHORIZED].*',
          responseTemplates: {
            'application/json': 'invalid request signature',
          },
        },
      ],
    });

    // Add a POST method for the Discord APIs.
    discordBotEventItems.addMethod('POST', discordBotIntegration, {
      apiKeyRequired: false,
      requestValidator: restApiValidator,
      methodResponses: [
        {
          statusCode: '200',
        },
        {
          statusCode: '401',
        },
      ],
    });

    const usagePlan = this.restApi.addUsagePlan("api-key-usage-plan", {
      name: "solana-index-discord-api-usage-plan",
      throttle: {
        rateLimit: 10,
        burstLimit: 2
      },
    });

    const apiKey = this.restApi.addApiKey("api-key", {
      apiKeyName: "solana-index-discord-api-key",
    });

    usagePlan.addApiKey(apiKey);
    usagePlan.addApiStage({ stage: this.restApi.deploymentStage });
  }
}
