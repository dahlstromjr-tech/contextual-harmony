import { AmbientUXStateMachine, UIState } from '../src/typescript/stateMachine';

describe('AmbientUXStateMachine', () => {
  let machine: AmbientUXStateMachine;

  beforeEach(() => {
    machine = new AmbientUXStateMachine();
  });

  test('should enter DORMANT state during deep focus (low AIS)', () => {
    const state = machine.evaluateSignal({ attentionImpactScore: 0.2, urgencyFlag: false, userExplicitlyRequested: false });
    expect(state).toBe(UIState.DORMANT);
  });

  test('should enter AMBIENT state under moderate cognitive load', () => {
    const state = machine.evaluateSignal({ attentionImpactScore: 0.6, urgencyFlag: false, userExplicitlyRequested: false });
    expect(state).toBe(UIState.AMBIENT);
  });

  test('should immediately override flow and enter ACTIVE state on urgencyFlag', () => {
    const state = machine.evaluateSignal({ attentionImpactScore: 0.1, urgencyFlag: true, userExplicitlyRequested: false });
    expect(state).toBe(UIState.ACTIVE);
  });

  test('should immediately override flow and enter ACTIVE state on explicit user request', () => {
    const state = machine.evaluateSignal({ attentionImpactScore: 0.1, urgencyFlag: false, userExplicitlyRequested: true });
    expect(state).toBe(UIState.ACTIVE);
  });
});