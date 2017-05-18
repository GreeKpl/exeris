import i18n from 'i18next';
import XHR from 'i18next-xhr-backend';
import {translate} from "react-i18next";
import Cache from 'i18next-localstorage-cache';


export const i18nize = component => {
  return translate(["common"], {
    wait: true,
  })(component);
};


const configuredI18n = i18n
  .use(XHR)
  .use(Cache)
  .init({
    lng: "en",
    fallbackLng: 'en',
    ns: ['common'],
    defaultNS: 'common',
    load: "languageOnly",
    debug: true,
    backend: {
      loadPath: "/player/static/{{lng}}.json",
      addPath: '/player/report_missing_tag',
    },
    saveMissing: true,
    prefix: "%{",
    suffix: "}",
    cache: {
      enabled: false
    },
    interpolation: {
      escapeValue: false,
      formatSeparator: ',',
      format: function (value, format, lng) {
        if (format === 'uppercase') return value.toUpperCase();
        return value;
      }
    }
  });

export default configuredI18n;
