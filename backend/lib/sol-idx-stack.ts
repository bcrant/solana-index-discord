import * as cdk from '@aws-cdk/core';
import * as apigateway from "@aws-cdk/aws-apigateway";
import * as events from "@aws-cdk/aws-events";
import * as eventTargets from "@aws-cdk/aws-events-targets";
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
      timeout: cdk.Duration.seconds(60), // can update this to anything under 15 minutes
      environment: {
        DISCORD_APP_NAME: process.env.DISCORD_APP_NAME as string,
        DISCORD_APP_ID: process.env.DISCORD_APP_ID as string,
        DISCORD_PUBLIC_KEY: process.env.DISCORD_PUBLIC_KEY as string,
        DISCORD_SECRET: process.env.DISCORD_SECRET as string
      },
    });

    const api = new apigateway.LambdaRestApi(this, "solana-index-api", {
      handler: discordFn,
      apiKeyRequired: true,
    });

    const apiKey = api.addApiKey("api-key", {
      apiKeyName: "solana-index-api-key",
    });

    const usagePlan = api.addUsagePlan("api-key-usage-plan", {
      name: "solana-index-api-usage-plan",
    });

    usagePlan.addApiKey(apiKey);
    usagePlan.addApiStage({ stage: api.deploymentStage });
  }
}
