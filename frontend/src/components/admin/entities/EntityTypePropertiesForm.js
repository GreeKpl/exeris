import React from "react";
import {ListGroup, ListGroupItem} from "react-bootstrap";
import {reduxForm, getFormValues, Field} from "redux-form/immutable";
import HorizontalFormInput from "../../commons/HorizontalFormInput";
import * as Immutable from "immutable";

const EntityTypePropertiesForm = ({fields, meta: {error}, propertyNames}) => {
  const allProperties = getAllOrEmpty(fields);
  const usedPropertyNames = allProperties.map(prop => prop.get("name"));
  return <div>
    <button type="button" onClick={() => fields.push(Immutable.fromJS({
      name: "Any",
      data: "",
    }))}>
      Add property
    </button>
    <ListGroup>
      {fields.map((property, index) => {
          return <EntityTypeProperty
            property={property}
            index={index}
            fields={fields}
            propertyNames={propertyNames.filter(propName =>
            !usedPropertyNames.contains(propName) || allProperties.get(index).get("name") === propName)}
            key={allProperties.get(index).get("name") + "_" + index}
          />
        }
      )}
    </ListGroup>
  </div>;
};

const getAllOrEmpty = fields => {
  if (fields.getAll() === undefined) {
    return Immutable.List();
  }
  return fields.getAll();
};

// TODO Fix issue when the json sometimes is not validated
const validJson = json => {
  try {
    console.log(">>>", json);
    const parsedJson = JSON.parse(json);
    return typeof(parsedJson) === "object" ? undefined : "It must be an object";
  } catch (e) {
    console.log("ERROR:", e);
    return "Not a valid JSON";
  }
};

const EntityTypeProperty = ({property, index, fields, propertyNames}) => {
  return <ListGroupItem>
    <button
      type="button"
      title="Remove Property"
      onClick={() => fields.remove(index)}
    >
      X
    </button>
    <Field name={`${property}.name`}
           component={HorizontalFormInput}
           componentClass="select"
           label="Property name"
           key="propertyName">
      {propertyNames.map(propertyName =>
        <option value={propertyName} key={propertyName}>{propertyName}</option>
      )}
    </Field>
    <Field name={`${property}.data`}
           component={HorizontalFormInput}
           componentClass="input"
           type="text"
           label=""
           placeholder="JSON data"
           validate={[validJson]}
           key="propertyData"
    />
  </ListGroupItem>
};

export default EntityTypePropertiesForm;
