import { Construct } from 'constructs';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import {
  ContentHandling,
  Cors,
  LambdaIntegration, 
  MethodLoggingLevel, 
  RequestValidator,
  RestApi,
} from 'aws-cdk-lib/aws-apigateway';
import { 
  Code,
  Function,
  LayerVersion,
  Runtime,
  Tracing
} from 'aws-cdk-lib/aws-lambda';
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

    const lambdaDepsLayer = new LayerVersion(this, props.functionName + '-layer', {
      code: Code.fromAsset('./lambda-layer', {
        bundling: {
          image: Runtime.PYTHON_3_9.bundlingImage,
          command: [
            'bash', '-c',
            String.raw`
              echo -e "[LOG] BUILDING DEPENDENCIES..." \
                && pip install -r requirements.txt -t /asset-output/python \
                && echo -e "[LOG] ZIPPING LAYER ARTIFACTS..." \
                && cp -au . /asset-output/python
            `
          ]
        }
      }),
      compatibleRuntimes: [Runtime.PYTHON_3_9]
    })

    lambdaPolicy.addActions("lambda:GetLayerVersion")
    lambdaPolicy.addResources(lambdaDepsLayer.layerVersionArn)

    this.lambdaFunction = new Function(this, props.functionName, {
      code: Code.fromAsset('./lambda'),
      functionName: props.functionName,
      handler: 'index.handler',
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
        DISCORD_GUILD_ID: process.env.DISCORD_GUILD_ID as string,
      },
      initialPolicy: [lambdaPolicy],
      layers: [lambdaDepsLayer],
      tracing: Tracing.ACTIVE,
    })

    const restApiName: string = "solana-index-discord-api"    
    this.restApi = new RestApi(this, restApiName, {
      restApiName: restApiName,
      deployOptions: {
        stageName: "prod",
        loggingLevel: MethodLoggingLevel.INFO,
        metricsEnabled: true,
        dataTraceEnabled: true,
        tracingEnabled: true,
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

    // User authentication endpoint configuration
    const discordBotEventItems = this.restApi.root.addResource("event", {
      defaultCorsPreflightOptions: {
        allowOrigins: [ 'https://discord.com' ],
        allowMethods: [ 'GET', 'POST', 'PATCH' ]
      },
    });

    const velocityTemplate = '{' +
      `"headers": {
          #foreach($param in $input.params().header.keySet())
          "$param": "$util.escapeJavaScript($input.params().header.get($param))"#if($foreach.hasNext),#end
          #end
        },` +
      `"jsonBody": "$util.escapeJavaScript($input.json("$"))",` +
      `"rawBody": "$util.escapeJavaScript($input.body).replace("\'", "'")",` +
      `"timestamp": "$input.params("x-signature-timestamp")",` +
      `"signature": "$input.params("x-signature-ed25519")"` +
    '}';

    // Transform our requests and responses as appropriate.
    const discordBotIntegration: LambdaIntegration = new LambdaIntegration(this.lambdaFunction, {
      proxy: false,
      requestTemplates: {
        'application/json': velocityTemplate
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
        rateLimit: 20,
        burstLimit: 10
      },
    });

    const apiKey = this.restApi.addApiKey("api-key", {
      apiKeyName: "solana-index-discord-api-key",
    });

    usagePlan.addApiKey(apiKey);
    usagePlan.addApiStage({ stage: this.restApi.deploymentStage });
  }
}
