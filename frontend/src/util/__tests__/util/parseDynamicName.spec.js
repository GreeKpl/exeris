import {parseHtmlToComponentsAndActions} from "../../parseDynamicName"
import {dynamicNamesReducer} from "../../../modules/dynamicNames";
import * as Immutable from "immutable";


describe('(util) htmlToComponent', () => {

  it('Should parse a single dynamic name in HTML without root.', () => {

    const html = "My name is <span class='dynamic_nameable' data-entity-id='char_john'>John</span> and I want to eat potatoes";
    const [parsedComponents, actionsForReducers] = parseHtmlToComponentsAndActions("CHAR_1", html);
    expect(parsedComponents[0]).toEqual("My name is ");
    expect(parsedComponents[1].props).toEqual({
      observerId: "CHAR_1",
      entityId: "char_john",
      children: null,
    });
    expect(parsedComponents[1].key).toEqual("1");
    expect(parsedComponents[2]).toEqual(" and I want to eat potatoes");
    expect(actionsForReducers.length).toEqual(1);

    const initialState = dynamicNamesReducer(undefined, {});
    const finalState = dynamicNamesReducer(initialState, actionsForReducers[0]);
    expect(finalState).toEqual(Immutable.fromJS({char_john: "John"}));
  });
});
