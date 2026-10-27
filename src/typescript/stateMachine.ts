export enum UIState { DORMANT = "DORMANT", AMBIENT = "AMBIENT", ACTIVE = "ACTIVE" }

export interface UserContextSignal {
  attentionImpactScore: number;
  urgencyFlag: boolean;
  userExplicitlyRequested: boolean;
}

export class AmbientUXStateMachine {
  private currentState: UIState = UIState.DORMANT;
  private readonly aisThreshold: number = 0.4;

  public evaluateSignal(signal: UserContextSignal): UIState {
    // If the user explicitly asks OR an external emergency flag triggers, 
    // break through immediately regardless of flow state.
    if (signal.userExplicitlyRequested || signal.urgencyFlag) {
      this.currentState = UIState.ACTIVE;
    } 
    // Otherwise, respect deep flow (Dormant)
    else if (signal.attentionImpactScore < this.aisThreshold) {
      this.currentState = UIState.DORMANT;
    } 
    // Moderate engagement (Ambient)
    else if (signal.attentionImpactScore < 0.8) {
      this.currentState = UIState.AMBIENT;
    } 
    // High cognitive load / idle
    else {
      this.currentState = UIState.ACTIVE;
    }

    return this.currentState;
  }
}
