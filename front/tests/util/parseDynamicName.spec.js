import {parseHtmlToComponent} from "../../src/util/parseDynamicName"
import {dynamicNamesReducer} from "../../src/modules/dynamicNames";
import * as Immutable from "immutable";


describe('(util) htmlToComponent', () => {

  it('Should parse a single dynamic name in HTML without root.', () => {

    const html = "My name is <span class='dynamic_nameable' data-entity-id='char_john'>John</span> and I want to eat potatoes";
    const [parsedComponents, actionsForReducers] = parseHtmlToComponent("CHAR_1", html);
    expect(parsedComponents[0]).to.equal("My name is ");
    expect(parsedComponents[1].props).to.deep.equal({
      observerId: "CHAR_1",
      entityId: "char_john",
      children: null,
    });
    expect(parsedComponents[1].key).to.equal("1");
    expect(parsedComponents[2]).to.equal(" and I want to eat potatoes");
    expect(actionsForReducers.length).to.equal(1);

    const initialState = dynamicNamesReducer(undefined, {});
    const finalState = dynamicNamesReducer(initialState, actionsForReducers[0]);
    expect(finalState).to.equal(Immutable.fromJS({char_john: "John"}));
  });
});
