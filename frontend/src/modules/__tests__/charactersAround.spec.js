import {
  updateCharactersAround,
  charactersAroundReducer,
  getIdsOfCharactersAround,
  fromCharactersAroundState,
  decoratedCharactersAroundReducer,
  requestCharactersAround,
  UPDATE_CHARACTERS_LIST,
} from "../charactersAround";
import * as Immutable from "immutable";
import {createMockStore, DependenciesStubber} from "../../../tests/testUtils";
import {__RewireAPI__ as parseDynamicNameRewire} from "../../util/parseDynamicName";
import {ADD_ENTITY_INFO} from "../entities";

describe('(charactersAround) charactersAroundReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(charactersAroundReducer(undefined, {})).toEqual(Immutable.List());
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS([{id: 1, name: "john"}]);
    let state = charactersAroundReducer(previousState, {});
    expect(state).toEqual(previousState);
  });

  it('Should update the charactersAround if an empty list is supplied.', () => {
    const previousState = Immutable.fromJS(
      [{id: 1, name: "john"}],
    );
    let state = charactersAroundReducer(previousState, updateCharactersAround(0, []));
    expect(state).toEqual(Immutable.List());
  });

  it('Should replace the state if a new list is supplied.', () => {
    const previousState = Immutable.fromJS(
      [{id: 1, name: "john"}],
    );
    let state = charactersAroundReducer(previousState, updateCharactersAround(0, [{id: 7, name: "ade"}]));
    expect(state).toEqual(Immutable.fromJS([{id: 7, name: "ade"}]));
  });

  it('Should update the charactersAround of a specified character.', () => {
    let state = decoratedCharactersAroundReducer(undefined, {});
    state = decoratedCharactersAroundReducer(state, updateCharactersAround("DEF", ["HEH", "AHA"]));
    state = decoratedCharactersAroundReducer(state, updateCharactersAround("3", ["HEJ", "HON"]));
    state = Immutable.Map({charactersAround: state});
    expect(getIdsOfCharactersAround(fromCharactersAroundState(state, "3")))
      .toEqual(Immutable.List(["HEJ", "HON"]));
    expect(getIdsOfCharactersAround(fromCharactersAroundState(state, "DEF")))
      .toEqual(Immutable.List(["HEH", "AHA"]));
  });

  it('Should request all characters around.', () => {
    const charId = "myChar";
    const char1Id = "char1";
    const char2Id = "char2";
    const char1 = {
      id: char1Id,
      name: "John",
    };
    const char2 = {
      id: char2Id,
      name: "Ally",
    };
    const store = createMockStore({}, [
      [
        char1, char2,
      ],
    ]);

    const dependencies = new DependenciesStubber(parseDynamicNameRewire, {
      extractActionsFromHtml: (characterId, html) => [],
    });

    store.dispatch(requestCharactersAround(charId));
    store.socketCalledWith("character.get_all_characters_around", charId);
    const actions = store.getActions();
    expect(actions).toHaveLength(3);
    expect(actions[0]).toEqual({
      type: ADD_ENTITY_INFO,
      entityInfo: char1,
      characterId: charId,
    });
    expect(actions[1]).toEqual({
      type: ADD_ENTITY_INFO,
      entityInfo: char2,
      characterId: charId,
    });
    expect(actions[2]).toEqual({
      type: UPDATE_CHARACTERS_LIST,
      characterIdsList: [char1Id, char2Id],
      characterId: charId,
    });
  });
});
