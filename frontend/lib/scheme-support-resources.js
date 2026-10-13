import data from "@/data/scheme-support-resources.json";

export const schemeSupportMetadata = {
  source: data.source,
  canonicalPackageDataset: data.canonicalPackageDataset,
  recordCount: data.recordCount,
  categoryCounts: data.categoryCounts,
};

export const schemeSupportResources = data.records;

export function getSchemeSupportResource(slug) {
  return schemeSupportResources.find((record) => record.slug === slug) || null;
}

export function getSchemeSupportCategories() {
  return Object.keys(schemeSupportMetadata.categoryCounts || {});
}

