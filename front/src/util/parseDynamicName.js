import React from 'react';
import {Parser as HtmlToReactParser, ProcessNodeDefinitions, IsValidNodeDefinitions} from 'html-to-react';
import * as Immutable from "immutable";
import DynamicNameContainer from "../../src/components/commons/DynamicNameContainer";
import {updateDynamicName} from "../modules/dynamicNames";

const htmlToReactParser = new HtmlToReactParser();

const isValidNode = function () {
  return true;
};

const processNodeDefinitions = new ProcessNodeDefinitions(React);


export const parseHtmlToComponents = (observerId, html) =>
  parseHtmlToComponentsAndActions(observerId, html)[0];

export const extractActionsFromHtml = (observerId, html) =>
  parseHtmlToComponentsAndActions(observerId, html)[1];


export const parseHtmlToComponentsAndActions = (observerId, html) => {
  // Instructions are processed in the order they're defined

  const actionsForReducers = [];
  const processingInstructions = [
    {
      shouldProcessNode: node => {
        if (!node.attribs) {
          return false;
        }
        const classNames = node.attribs['class'];
        if (!classNames) {
          return false;
        }
        return Immutable.fromJS(classNames.split(" ")).includes("dynamic_nameable");
      },
      processNode: (node, children, index) => {
        const entityId = node.attribs['data-entity-id'];
        const entityName = children[0]; // it should be a single text node
        actionsForReducers.push(updateDynamicName(observerId, entityId, entityName));

        return React.createElement(DynamicNameContainer, {
          key: index,
          observerId: observerId,
          entityId: entityId,
        }, null);
      }
    },
    {
      shouldProcessNode: node => {
        return true;
      },
      processNode: processNodeDefinitions.processDefaultNode,
    },
  ];

  const parsedComponents = htmlToReactParser.parseWithInstructions(
    html, IsValidNodeDefinitions.alwaysValid, processingInstructions);

  return [parsedComponents, actionsForReducers];
};
