import {
  travelReducer,
  canBeControlled,
  getMovementAction,
  UPDATE_TRAVEL_STATE, incrementTravelStateTick, getTickId
} from "../../src/modules/travel";
import * as Immutable from "immutable";

describe('(character) travelReducer', () => {

  it('Should initialize with initial state of empty list.', () => {
    expect(travelReducer(undefined, {})).to.equal(Immutable.fromJS({
      "canBeControlled": false,
      "travelTick": 0,
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      "canBeControlled": true,
      "travelTick": 0,
    });
    let state = travelReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  it('Should update travel state.', () => {
    let state = travelReducer(undefined, {});
    expect(canBeControlled(state)).to.equal(false);
    expect(getMovementAction(state)).to.equal(null);

    state = travelReducer(state, {
      type: UPDATE_TRAVEL_STATE,
      travelData: {
        "canBeControlled": true,
        "movementAction": "DEF",
      },
      characterId: "ABC",
    });
    expect(canBeControlled(state)).to.equal(true);
    expect(getMovementAction(state)).to.equal("DEF");
  });

  it('Should update travel tick.', () => {
    let state = travelReducer(undefined, {});

    state = travelReducer(state, incrementTravelStateTick("DEF"));
    expect(getTickId(state)).to.equal(1);
    state = travelReducer(state, incrementTravelStateTick("DEF"));
    expect(getTickId(state)).to.equal(2);
  });
});
