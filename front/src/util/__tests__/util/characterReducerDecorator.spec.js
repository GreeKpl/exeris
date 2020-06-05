import {characterReducerDecorator} from "../../characterReducerDecorator";
import * as Immutable from "immutable";

describe('(util) characterReducerDecorator', () => {

  const noopReducer = (state = "NOOP", action) => state;

  it('Should initialize with initial state of empty map.', () => {

    const characterNoopReducer = characterReducerDecorator(noopReducer);
    expect(characterNoopReducer(undefined, {})).toEqual(Immutable.Map());
  });

  it('Should create entry in state with initial state for decorated reducer.', () => {
    const characterNoopReducer = characterReducerDecorator(noopReducer);
    expect(characterNoopReducer(undefined, {
      type: "ABC",
      characterId: 1
    }))
      .toEqual(Immutable.Map({"1": "NOOP"}));
  });

  it('Should create entry in state with initial state for decorated reducer and reduce an action.', () => {
    const counterReducer = (state = 0, action) => {
      if (action.type === "INCREMENT") {
        return state + 1;
      }
      return state;
    };

    const incrementAction = (characterId) => {
      return {
        type: "INCREMENT",
        characterId: characterId,
      }
    };

    const characterCounterReducer = characterReducerDecorator(counterReducer);

    let stateAfterReduction = characterCounterReducer(undefined, incrementAction(1));
    expect(stateAfterReduction).toEqual(Immutable.Map({"1": 1}));

    stateAfterReduction = characterCounterReducer(stateAfterReduction, incrementAction(1));
    expect(stateAfterReduction).toEqual(Immutable.Map({"1": 2}));

    stateAfterReduction = characterCounterReducer(stateAfterReduction, incrementAction("D"));
    expect(stateAfterReduction).toEqual(Immutable.Map({"1": 2, "D": 1}));
  });
});
