import {
  travelReducer,
  canBeControlled,
  getMovementAction,
  UPDATE_TRAVEL_STATE, incrementTravelStateTick, getTickId,
  requestTravelState, changeMovementDirection, stopMovement
} from "../travel";
import * as Immutable from "immutable";
import {createMockStore} from "../../../tests/testUtils";

describe('(character) travelReducer', () => {

  it('Should initialize with initial state of empty list.', () => {
    expect(travelReducer(undefined, {})).toEqual(Immutable.fromJS({
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
    expect(state).toEqual(previousState);
  });

  it('Should update travel state.', () => {
    let state = travelReducer(undefined, {});
    expect(canBeControlled(state)).toEqual(false);
    expect(getMovementAction(state)).toEqual(null);

    state = travelReducer(state, {
      type: UPDATE_TRAVEL_STATE,
      travelData: {
        "canBeControlled": true,
        "movementAction": "DEF",
      },
      characterId: "ABC",
    });
    expect(canBeControlled(state)).toEqual(true);
    expect(getMovementAction(state)).toEqual("DEF");
  });

  it('Should update travel tick.', () => {
    let state = travelReducer(undefined, {});

    state = travelReducer(state, incrementTravelStateTick("DEF"));
    expect(getTickId(state)).toEqual(1);
    state = travelReducer(state, incrementTravelStateTick("DEF"));
    expect(getTickId(state)).toEqual(2);
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
      expect(actions).toHaveLength(1);
      expect(actions[0]).toEqual(updateTravelStateAction);
    });

    it('Should change travel direction which also requests travel state from the backend.', () => {
      const store = createMockStore({}, {
        "character.move_in_direction": [],
        "character.get_movement_info": [travelData],
      });
      store.dispatch(changeMovementDirection(charId, 100));
      const actions = store.getActions();
      expect(actions).toHaveLength(1);
      expect(actions[0]).toEqual(updateTravelStateAction);
    });

    it('Should stop movement which also requests travel state from the backend.', () => {
      const store = createMockStore({}, {
        "character.stop_movement": [],
        "character.get_movement_info": [travelData],
      });
      store.dispatch(stopMovement(charId));
      const actions = store.getActions();
      expect(actions).toHaveLength(1);
      expect(actions[0]).toEqual(updateTravelStateAction);
    });
  });
});
