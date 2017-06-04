import {ActionDetailsRaw} from "../../../src/components/character/actions/ActionDetailsContainer";
import * as Immutable from "immutable";
import {shallow, mount} from "enzyme";
import * as React from "react";

describe('(component) ActionDetails', () => {

  it('Should render empty action details when no data specified.', () => {
    const testedComponent = shallow(<ActionDetailsRaw recipeDetails={Immutable.Map()}/>);
    expect(testedComponent.isEmptyRender()).to.equal(true);
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

    expect(testedComponent.find("RequirementInfo")).to.have.length(5);
    expect(testedComponent.find("Button").prop("disabled")).to.equal(false);
  });

  it('Should render an error message and make the submit button unavailable.', () => {
    const recipeDetails = Immutable.fromJS({
      requiredFormInputs: [],
      errorMessages: ["Too little potatoes"],
      requiredDays: 3,
    });
    const testedComponent = shallow(<ActionDetailsRaw recipeDetails={recipeDetails}/>);
    expect(testedComponent.find("ListGroupItem")).to.have.length(1);
    expect(testedComponent.find("ListGroupItem").prop("children")).to.equal("Too little potatoes");
    expect(testedComponent.find("Button").prop("disabled")).to.equal(true);
  });
});
