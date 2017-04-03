import {
  DETAILS_COMBAT, DETAILS_CHARACTER,
  applyCharacterDetails,
  applyCombatDetails,
  closeTopPanel,
  getDetailsType,
  fromTopPanelState,
  topPanelReducer,
  decoratedTopPanelReducer, getDetailsTarget
} from "../../src/modules/topPanel";
import * as Immutable from "immutable";

describe('(topPanel) topPanelReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(topPanelReducer(undefined, {})).to.equal(Immutable.fromJS({
      type: null,
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = topPanelReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  it('Should update the state when character details are supplied.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = topPanelReducer(previousState, applyCharacterDetails(0, "DEF"));
    expect(state).to.equal(Immutable.fromJS({
        type: DETAILS_CHARACTER,
        targetId: "DEF",
      }
    ));
  });

  it('Should update the state when combat details are supplied.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = topPanelReducer(previousState, applyCombatDetails(0, "DEF"));
    expect(state).to.equal(Immutable.fromJS({
      type: DETAILS_COMBAT,
      targetId: "DEF",
    }));
  });

  it('Should clear the state on close action.', () => {
    const previousState = Immutable.fromJS({
      type: DETAILS_CHARACTER,
      id: "DEF",
      name: "John",
      locationName: "Place",
      locationId: "123",
      workIntent: "",
    });
    let state = topPanelReducer(previousState, closeTopPanel(0));
    expect(state).to.equal(Immutable.fromJS({
      type: null,
    }));
  });

  it('Should completely remove old state when replaced by a new state.', () => {
    const previousState = Immutable.fromJS({
      type: DETAILS_CHARACTER,
      targetId: "DEF",
    });
    let state = topPanelReducer(previousState, applyCombatDetails(0, "DEF"));
    expect(state).to.equal(Immutable.fromJS({
      type: DETAILS_COMBAT,
      targetId: "DEF",
    }));
  });

  it('Should update the speech of a specified character.', () => {
    let state = decoratedTopPanelReducer(undefined, {});
    state = decoratedTopPanelReducer(state, applyCombatDetails("HEHE", "DEF"));
    const globalState = Immutable.Map({topPanel: state});

    expect(getDetailsType(fromTopPanelState(globalState, "HEHE"))).to.equal(DETAILS_COMBAT);
    expect(getDetailsTarget(fromTopPanelState(globalState, "HEHE"))).to.equal("DEF");
    expect(getDetailsTarget(fromTopPanelState(globalState, "MISSING_CHAR"))).to.equal(null);
  });
});
