#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { SolanaIndexStack } from '../lib/sol-idx-stack';
import * as dotenv from "dotenv";
dotenv.config()

const app = new cdk.App();
new SolanaIndexStack(app, 'SolanaIndex', {
    env: { region: "us-east-1" },
});
