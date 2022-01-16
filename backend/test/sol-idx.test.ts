import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as SolanaIndex from '../lib/sol-idx-stack.ts';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new SolanaIndex.SolanaIndexStack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
