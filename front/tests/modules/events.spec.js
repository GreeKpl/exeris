import {
  eventsReducer,
  getAllEvents,
  fromEventsState,
  updateEventsList,
  appendToEventsList,
  decoratedEventsReducer
} from "../../src/modules/events";
import * as Immutable from "immutable";

describe('(events) eventsReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(eventsReducer(undefined, {})).to.equal(Immutable.fromJS({
      eventsList: [],
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      eventsList: [{"id": 1, "text": "abc"}],
    });
    let state = eventsReducer(previousState, {});
    expect(state).to.equal(previousState);
  });


  it('Should update the eventsList if an empty list is supplied.', () => {
    const previousState = Immutable.fromJS({
      eventsList: [{"id": 1, "text": "abc"}],
    });
    let state = eventsReducer(previousState, updateEventsList(0, []));
    expect(state).to.equal(previousState.setIn(["eventsList"], Immutable.List()));
  });

  it('Should replace the state if a new list is supplied.', () => {
    const previousState = Immutable.fromJS({
      eventsList: [{"id": 1, "text": "abc"}],
    });
    let state = eventsReducer(previousState, updateEventsList(0, [{id: 11, text: "ade"}]));
    expect(state).to.equal(previousState.setIn(["eventsList"],
      Immutable.fromJS([{id: 11, text: "ade"}])));
  });

  it('Should update the eventsList if a list is appended.', () => {
    const previousState = Immutable.fromJS({
      eventsList: [{"id": 1, "text": "abc"}],
    });
    let state = eventsReducer(previousState, appendToEventsList(0, [{id: 11, text: "ade"}]));
    expect(state).to.equal(previousState.setIn(["eventsList"],
      Immutable.fromJS([{"id": 1, "text": "abc"}, {id: 11, text: "ade"}])));
  });

  it('Should update the eventsList if a list is appended.', () => {
    const state = Immutable.fromJS({
      eventsList: [{"id": 1, "text": "abc"}, {id: 11, text: "ade"}],
    });

    expect(getAllEvents(state)).to.equal(Immutable.fromJS([
      {"id": 1, "text": "abc"},
      {id: 11, text: "ade"}
    ]));
  });

  it('Should update the eventsList of a specified character.', () => {
    let state = decoratedEventsReducer(undefined, {});
    state = decoratedEventsReducer(state, updateEventsList("DEF", [{"id": 1, "text": "abc"}]));
    state = decoratedEventsReducer(state, updateEventsList("3", [{id: 11, text: "ade"}]));
    state = Immutable.Map({events: state});
    expect(getAllEvents(fromEventsState(state, "3"))).to.equal(Immutable.fromJS([
      {id: 11, text: "ade"}
    ]));
    expect(getAllEvents(fromEventsState(state, "DEF"))).to.equal(Immutable.fromJS([
      {"id": 1, "text": "abc"},
    ]));
  });
});
