import { AmbientUXStateMachine, UIState } from '../src/typescript/stateMachine';

describe('AmbientUXStateMachine', () => {
  let sm: AmbientUXStateMachine;

  beforeEach(() => {
    sm = new AmbientUXStateMachine();
  });

  it('should remain DORMANT when AIS is below threshold and no flags are set', () => {
    const state = sm.evaluateSignal({
      attentionImpactScore: 0.2,
      urgencyFlag: false,
      userExplicitlyRequested: false
    });
    expect(state).toBe(UIState.DORMANT);
  });

  it('should transition to AMBIENT when AIS is moderate', () => {
    const state = sm.evaluateSignal({
      attentionImpactScore: 0.6,
      urgencyFlag: false,
      userExplicitlyRequested: false
    });
    expect(state).toBe(UIState.AMBIENT);
  });

  it('should override and transition to ACTIVE when user explicitly requests', () => {
    const state = sm.evaluateSignal({
      attentionImpactScore: 0.1, // deep flow
      urgencyFlag: false,
      userExplicitlyRequested: true // explicit bypass
    });
    expect(state).toBe(UIState.ACTIVE);
  });
});
