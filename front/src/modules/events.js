import * as Immutable from "immutable";
import {characterReducerDecorator} from "../util/characterReducerDecorator";

export const UPDATE_EVENTS_LIST = "exeris-front/events/UPDATE_EVENTS_LIST";
export const APPEND_TO_EVENTS_LIST = "exeris-front/events/APPEND_TO_EVENTS_LIST";

export const setUpSocketioListeners = (dispatch, socket) => {
  socket.on("character.new_event", (characterId, event) => {
    dispatch(appendToEventsList(characterId, [event]));
  });
};

export const requestAllEvents = (characterId) => {
  return (dispatch, getState, socket) => {
    socket.request("character.get_all_events", characterId, eventsList => {
      dispatch(updateEventsList(characterId, eventsList));
    });
  }
};

export const updateEventsList = (characterId, eventsList) => {
  return {
    type: UPDATE_EVENTS_LIST,
    eventsList: eventsList,
    characterId: characterId,
  };
};

export const appendToEventsList = (characterId, eventsList) => {
  return {
    type: APPEND_TO_EVENTS_LIST,
    eventsList: eventsList,
    characterId: characterId,
  };
};


export const eventsReducer = (state = Immutable.fromJS({eventsList: []}), action) => {
  switch (action.type) {
    case UPDATE_EVENTS_LIST:
      return state.set("eventsList", Immutable.fromJS(action.eventsList));
    case APPEND_TO_EVENTS_LIST:
      return state.updateIn(["eventsList"], oldList => oldList.concat(Immutable.fromJS(action.eventsList)));
    default:
      return state;
  }
};

export const decoratedEventsReducer = characterReducerDecorator(eventsReducer);

export const getAllEvents = state => state.get("eventsList", []);

export const fromEventsState = (state, characterId) => state.getIn(["events", characterId], Immutable.Map());
