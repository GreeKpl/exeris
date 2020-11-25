import i18n from 'i18next';
import XHR from 'i18next-xhr-backend';
import {withTranslation} from "react-i18next";
import Cache from 'i18next-localstorage-cache';


export const i18nize = component => {
  return withTranslation(["common"], {
    wait: true,
  })(component);
};


const configuredI18n = i18n
  .use(XHR)
  .use(Cache);

configuredI18n.init({
    lng: "en",
    fallbackLng: 'en',
    ns: ['common'],
    defaultNS: 'common',
    load: "languageOnly",
    debug: true,
    backend: {
      loadPath: "/static/{{lng}}.json",
      addPath: '/report_missing_tag',
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
    },
    react: {
      useSuspense: false,
    },
  });

export default configuredI18n;
