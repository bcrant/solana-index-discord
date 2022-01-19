#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SolIdxStack } from '../lib/sol-idx-stack';

export const lambdaApiStackName = "SolIdxStack"
export const lambdaFunctionName = "solana-index-discord-fn"

const app = new cdk.App();
new SolIdxStack(app, lambdaApiStackName, {
  functionName: lambdaFunctionName,
  env: { region: "us-east-1" },
});
