import {ActionDetailsRaw} from "../ActionDetailsContainer";
import * as Immutable from "immutable";
import {shallow, mount} from "enzyme";
import * as React from "react";

describe('(component) ActionDetails', () => {

  it('Should render empty action details when no data specified.', () => {
    const testedComponent = shallow(<ActionDetailsRaw recipeDetails={Immutable.Map()}/>);
    expect(testedComponent.isEmptyRender()).toEqual(true);
  });

  it('Should render basic action details and allow clicking submit.', () => {
    const recipeDetails = Immutable.fromJS({
      requiredFormInputs: [
        {
          type: "AmountInput",
          name: "amount",
        },
      ],
      errorMessages: [],
      requiredDays: 3,
    });

    const testedComponent = shallow(<ActionDetailsRaw recipeDetails={recipeDetails}/>);

    expect(testedComponent.find("RequirementInfo")).toHaveLength(5);
    expect(testedComponent.find("Button").prop("disabled")).toEqual(false);
  });

  it('Should render an error message and make the submit button unavailable.', () => {
    const recipeDetails = Immutable.fromJS({
      requiredFormInputs: [],
      errorMessages: ["Too little potatoes"],
      requiredDays: 3,
    });
    const testedComponent = shallow(<ActionDetailsRaw recipeDetails={recipeDetails}/>);
    expect(testedComponent.find("ListGroupItem")).toHaveLength(1);
    expect(testedComponent.find("ListGroupItem").prop("children")).toEqual("Too little potatoes");
    expect(testedComponent.find("Button").prop("disabled")).toEqual(true);
  });
});
