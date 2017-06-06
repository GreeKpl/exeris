import {
  travelReducer,
  canBeControlled,
  getMovementAction,
  UPDATE_TRAVEL_STATE, incrementTravelStateTick, getTickId,
  requestTravelState, changeMovementDirection, stopMovement
} from "../../src/modules/travel";
import * as Immutable from "immutable";
import {createMockStore} from "../testUtils";

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

  describe("Asynchronous socketio actions", () => {
    const travelData = {id: 123};
    const charId = "DEF";
    const updateTravelStateAction = {
      type: UPDATE_TRAVEL_STATE,
      travelData: travelData,
      characterId: charId,
    };

    it('Should request travel state from the backend.', () => {
      const store = createMockStore({}, [travelData]);
      store.dispatch(requestTravelState(charId));
      const actions = store.getActions();
      expect(actions).to.have.length(1);
      expect(actions[0]).to.deep.equal(updateTravelStateAction);
    });

    it('Should change travel direction which also requests travel state from the backend.', () => {
      const store = createMockStore({}, {
        "character.move_in_direction": [],
        "character.get_movement_info": [travelData],
      });
      store.dispatch(changeMovementDirection(charId, 100));
      const actions = store.getActions();
      expect(actions).to.have.length(1);
      expect(actions[0]).to.deep.equal(updateTravelStateAction);
    });

    it('Should stop movement which also requests travel state from the backend.', () => {
      const store = createMockStore({}, {
        "character.stop_movement": [],
        "character.get_movement_info": [travelData],
      });
      store.dispatch(stopMovement(charId));
      const actions = store.getActions();
      expect(actions).to.have.length(1);
      expect(actions[0]).to.deep.equal(updateTravelStateAction);
    });
  });
});
