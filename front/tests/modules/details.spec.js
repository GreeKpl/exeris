import {
  PANEL_COMBAT, PANEL_CHARACTER,
  applyCharacterDetails,
  applyCombatDetails,
  closeDetails,
  getDetailsType,
  fromDetailsState,
  detailsReducer,
  decoratedDetailsReducer, getDetailsTarget
} from "../../src/modules/details";
import * as Immutable from "immutable";

describe('(details) detailsReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(detailsReducer(undefined, {})).to.equal(Immutable.fromJS({
      type: null,
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = detailsReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  it('Should update the state when character details are supplied.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = detailsReducer(previousState, applyCharacterDetails(0, "DEF"));
    expect(state).to.equal(Immutable.fromJS({
        type: PANEL_CHARACTER,
        targetId: "DEF",
      }
    ));
  });

  it('Should update the state when combat details are supplied.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = detailsReducer(previousState, applyCombatDetails(0, "DEF"));
    expect(state).to.equal(Immutable.fromJS({
      type: PANEL_COMBAT,
      targetId: "DEF",
    }));
  });

  it('Should clear the state on close action.', () => {
    const previousState = Immutable.fromJS({
      type: PANEL_CHARACTER,
      id: "DEF",
      name: "John",
      locationName: "Place",
      locationId: "123",
      workIntent: "",
    });
    let state = detailsReducer(previousState, closeDetails(0));
    expect(state).to.equal(Immutable.fromJS({
      type: null,
    }));
  });

  it('Should completely remove old state when replaced by a new state.', () => {
    const previousState = Immutable.fromJS({
      type: PANEL_CHARACTER,
      targetId: "DEF",
    });
    let state = detailsReducer(previousState, applyCombatDetails(0, "DEF"));
    expect(state).to.equal(Immutable.fromJS({
      type: PANEL_COMBAT,
      targetId: "DEF",
    }));
  });

  it('Should update the speech of a specified character.', () => {
    let state = decoratedDetailsReducer(undefined, {});
    state = decoratedDetailsReducer(state, applyCombatDetails("HEHE", "DEF"));
    const globalState = Immutable.Map({details: state});

    expect(getDetailsType(fromDetailsState(globalState, "HEHE"))).to.equal(PANEL_COMBAT);
    expect(getDetailsTarget(fromDetailsState(globalState, "HEHE"))).to.equal("DEF");
    expect(getDetailsTarget(fromDetailsState(globalState, "MISSING_CHAR"))).to.equal(null);
  });
});
