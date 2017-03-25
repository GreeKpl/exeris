import * as Immutable from "immutable";
import {characterReducerDecorator} from "../util/characterReducerDecorator";
import socket from "../util/server";
import {extractActionsFromHtml} from "../util/parseDynamicName";

export const UPDATE_TRAVEL_STATE = "exeris-front/travel/UPDATE_TRAVEL_STATE";


export const requestTravelState = characterId => {
  return dispatch => {
    socket.request("character.get_movement_info", characterId, travelData => {
      dispatch(updateTravelState(characterId, travelData));
    });
  }
};

export const updateTravelState = (characterId, travelData) => {
  return dispatch => {

    if (travelData.movementAction) {
      const actionsToUpdateNames = extractActionsFromHtml(characterId, travelData.movementAction);
      actionsToUpdateNames.forEach(action => dispatch(action));
    }

    console.log(UPDATE_TRAVEL_STATE, travelData);
    dispatch({
      type: UPDATE_TRAVEL_STATE,
      travelData: travelData,
      characterId: characterId,
    });
  }
};

export const changeMovementDirection = (characterId, direction) => {
  return dispatch => {
    socket.request("character.move_in_direction", characterId, direction, () =>
      dispatch(requestTravelState(characterId))
    );
  };
};

export const stopMovement = characterId => {
  return dispatch => {
    socket.request("character.stop_movement", characterId, () =>
      dispatch(requestTravelState(characterId))
    );
  };
};

export const travelReducer = (state = Immutable.fromJS({
  "canBeControlled": false,
}), action) => {
  switch (action.type) {
    case UPDATE_TRAVEL_STATE:
      return Immutable.fromJS(action.travelData);
    default:
      return state;
  }
};

export const decoratedTravelReducer = characterReducerDecorator(travelReducer);

export const canBeControlled = state => state.get("canBeControlled", false);

export const getMovementAction = state => state.get("movementAction", null);

export const fromTravelState = (state, characterId) =>
  state.getIn(["travel", characterId], Immutable.Map());
