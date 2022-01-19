import * as cdk from '@aws-cdk/core';
import * as apigateway from "@aws-cdk/aws-apigateway";
import * as lambda from "@aws-cdk/aws-lambda";
import { PythonFunction } from "@aws-cdk/aws-lambda-python";


export class SolanaIndexStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)

    const discordFn = new PythonFunction(this, "discord-fn", {
      functionName: "solana-index-discord",
      entry: "./lambda/discord",
      // index: "", // will default to index.py but you can override that here
      // handler: "", // will default to handler but you can override that here
      runtime: lambda.Runtime.PYTHON_3_9,
      timeout: cdk.Duration.seconds(20), // can update this to anything under 15 minutes
      environment: {
        DISCORD_APP_NAME: process.env.DISCORD_APP_NAME as string,
        DISCORD_APP_ID: process.env.DISCORD_APP_ID as string,
        DISCORD_PUBLIC_KEY: process.env.DISCORD_PUBLIC_KEY as string,
        DISCORD_SECRET: process.env.DISCORD_SECRET as string,
        DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN as string,
        DISCORD_BOT_PERMISSIONS: process.env.DISCORD_BOT_PERMISSIONS as string,
      },
    });

    const api = new apigateway.RestApi(this, "solana-index-api", {
      restApiName: "solana-index-api",
      deployOptions: {
        stageName: "prod",
      },
    });

    const discord = api.root.addResource("discord");

    discord.addMethod("POST", new apigateway.LambdaIntegration(discordFn), {
      apiKeyRequired: true,
    });

    const apiKey = api.addApiKey("api-key", {
      apiKeyName: "solana-index-api-key",
    });

    const usagePlan = api.addUsagePlan("api-key-usage-plan", {
      name: "solana-index-api-usage-plan",
      throttle: {
        rateLimit: 10,
        burstLimit: 2
      },
    });

    usagePlan.addApiKey(apiKey);
    usagePlan.addApiStage({ stage: api.deploymentStage });
  }
}
