import {
  updateCharactersAround,
  charactersAroundReducer,
  getIdsOfCharactersAround,
  fromCharactersAroundState,
  decoratedCharactersAroundReducer,
  requestCharactersAround,
  UPDATE_CHARACTERS_LIST,
} from "../../src/modules/charactersAround";
import * as Immutable from "immutable";
import {createMockStore, DependenciesStubber} from "../testUtils";
import {__RewireAPI__ as parseDynamicNameRewire} from "./../../src/util/parseDynamicName";
import {ADD_ENTITY_INFO} from "../../src/modules/entities";

describe('(charactersAround) charactersAroundReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(charactersAroundReducer(undefined, {})).to.equal(Immutable.List());
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS([{id: 1, name: "john"}]);
    let state = charactersAroundReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  it('Should update the charactersAround if an empty list is supplied.', () => {
    const previousState = Immutable.fromJS(
      [{id: 1, name: "john"}],
    );
    let state = charactersAroundReducer(previousState, updateCharactersAround(0, []));
    expect(state).to.equal(Immutable.List());
  });

  it('Should replace the state if a new list is supplied.', () => {
    const previousState = Immutable.fromJS(
      [{id: 1, name: "john"}],
    );
    let state = charactersAroundReducer(previousState, updateCharactersAround(0, [{id: 7, name: "ade"}]));
    expect(state).to.equal(Immutable.fromJS([{id: 7, name: "ade"}]));
  });

  it('Should update the charactersAround of a specified character.', () => {
    let state = decoratedCharactersAroundReducer(undefined, {});
    state = decoratedCharactersAroundReducer(state, updateCharactersAround("DEF", ["HEH", "AHA"]));
    state = decoratedCharactersAroundReducer(state, updateCharactersAround("3", ["HEJ", "HON"]));
    state = Immutable.Map({charactersAround: state});
    expect(getIdsOfCharactersAround(fromCharactersAroundState(state, "3")))
      .to.equal(Immutable.List(["HEJ", "HON"]));
    expect(getIdsOfCharactersAround(fromCharactersAroundState(state, "DEF")))
      .to.equal(Immutable.List(["HEH", "AHA"]));
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
    dependencies.rewireAll();
    store.dispatch(requestCharactersAround(charId));
    store.socketCalledWith("character.get_all_characters_around", charId);
    const actions = store.getActions();
    expect(actions).to.have.length(3);
    expect(actions[0]).to.deep.equal({
      type: ADD_ENTITY_INFO,
      entityInfo: char1,
      characterId: charId,
    });
    expect(actions[1]).to.deep.equal({
      type: ADD_ENTITY_INFO,
      entityInfo: char2,
      characterId: charId,
    });
    expect(actions[2]).to.deep.equal({
      type: UPDATE_CHARACTERS_LIST,
      characterIdsList: [char1Id, char2Id],
      characterId: charId,
    });
    dependencies.unwireAll();
  });
});
