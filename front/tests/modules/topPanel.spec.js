import {
  DETAILS_COMBAT, DETAILS_CHARACTER,
  applyCharacterDetails,
  applyCombatDetails,
  closeTopPanel,
  getDetailsData,
  getDetailsType,
  fromTopPanelState,
  topPanelReducer,
  decoratedTopPanelReducer
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
    let state = topPanelReducer(previousState, applyCharacterDetails(0, {
      id: "DEF",
      name: "John",
      locationName: "Place",
      locationId: "123",
      workIntent: "",
    }));
    expect(state).to.equal(Immutable.fromJS({
        type: DETAILS_CHARACTER,
        id: "DEF",
        name: "John",
        locationName: "Place",
        locationId: "123",
        workIntent: "",
      }
    ));
  });

  it('Should update the state when combat details are supplied.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = topPanelReducer(previousState, applyCombatDetails(0, {
      id: "DEF",
      attackers: [{id: "HEL", name: "Eddy", stance: "offensive", damage: 0.3, recordedDamage: 0.1}],
      defenders: [{id: "ICH", name: "Ally", stance: "offensive", damage: 0.1, recordedDamage: 0.5},
        {id: "BIN", name: "Kelly", stance: "retreat", damage: 0.2, recordedDamage: 0.15}],
    }));
    expect(state).to.equal(Immutable.fromJS({
      type: DETAILS_COMBAT,
      id: "DEF",
      attackers: [{id: "HEL", name: "Eddy", stance: "offensive", damage: 0.3, recordedDamage: 0.1}],
      defenders: [{id: "ICH", name: "Ally", stance: "offensive", damage: 0.1, recordedDamage: 0.5},
        {id: "BIN", name: "Kelly", stance: "retreat", damage: 0.2, recordedDamage: 0.15}],
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
      id: "DEF",
      name: "John",
      locationName: "Place",
      locationId: "123",
      workIntent: "",
    });
    let state = topPanelReducer(previousState, applyCombatDetails(0, {
      id: "DEF",
      attackers: [{id: "HEL", name: "Eddy", stance: "offensive", damage: 0.3, recordedDamage: 0.1}],
      defenders: [{id: "ICH", name: "Ally", stance: "offensive", damage: 0.1, recordedDamage: 0.5}],
    }));
    expect(state).to.equal(Immutable.fromJS({
      type: DETAILS_COMBAT,
      id: "DEF",
      attackers: [{id: "HEL", name: "Eddy", stance: "offensive", damage: 0.3, recordedDamage: 0.1}],
      defenders: [{id: "ICH", name: "Ally", stance: "offensive", damage: 0.1, recordedDamage: 0.5}],
    }));
  });

  it('Should update the speech of a specified character.', () => {
    let state = decoratedTopPanelReducer(undefined, {});
    state = decoratedTopPanelReducer(state, applyCombatDetails("HEHE", {
      id: "DEF",
      attackers: [{id: "HEL", name: "Eddy", stance: "offensive", damage: 0.3, recordedDamage: 0.1}],
      defenders: [{id: "ICH", name: "Ally", stance: "offensive", damage: 0.1, recordedDamage: 0.5}],
    }));
    const globalState = Immutable.Map({topPanel: state});

    expect(getDetailsType(fromTopPanelState(globalState, "HEHE"))).to.equal(DETAILS_COMBAT);
    expect(getDetailsData(fromTopPanelState(globalState, "HEHE"))).to.equal(Immutable.fromJS({
      id: "DEF",
      attackers: [{id: "HEL", name: "Eddy", stance: "offensive", damage: 0.3, recordedDamage: 0.1}],
      defenders: [{id: "ICH", name: "Ally", stance: "offensive", damage: 0.1, recordedDamage: 0.5}],
    }));
    expect(getDetailsData(fromTopPanelState(globalState, "MISSING_CHAR"))).to.equal(Immutable.Map());
  });
});
