-- output from running sqlite3 .schema on a .lrcat file

CREATE TABLE Adobe_variablesTable (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    name,
    type,
    value NOT NULL DEFAULT ''
);
CREATE TABLE Adobe_variables (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    name,
    value
);
CREATE INDEX index_Adobe_variables_name ON Adobe_variables( name );
CREATE TABLE AgFolderContent (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    containingFolder INTEGER NOT NULL DEFAULT 0,
    content,
    name,
    owningModule
);
CREATE INDEX index_AgFolderContent_owningModule ON AgFolderContent( owningModule );
CREATE INDEX index_AgFolderContent_containingFolder ON AgFolderContent( containingFolder );
CREATE TABLE Adobe_AdditionalMetadata (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    additionalInfoSet INTEGER NOT NULL DEFAULT 0,
    embeddedXmp INTEGER NOT NULL DEFAULT 0,
    externalXmpIsDirty INTEGER NOT NULL DEFAULT 0,
    image INTEGER,
    incrementalWhiteBalance INTEGER NOT NULL DEFAULT 0,
    internalXmpDigest,
    isRawFile INTEGER NOT NULL DEFAULT 0,
    lastSynchronizedHash,
    lastSynchronizedTimestamp NOT NULL DEFAULT -63113817600,
    metadataPresetID,
    metadataVersion,
    monochrome INTEGER NOT NULL DEFAULT 0,
    xmp NOT NULL DEFAULT ''
);
CREATE INDEX index_Adobe_AdditionalMetadata_imageAndStatus ON Adobe_AdditionalMetadata( image, externalXmpIsDirty );
CREATE TABLE AgMetadataSearchIndex (
    id_local INTEGER PRIMARY KEY,
    exifSearchIndex NOT NULL DEFAULT '',
    image INTEGER,
    iptcSearchIndex NOT NULL DEFAULT '',
    otherSearchIndex NOT NULL DEFAULT '',
    searchIndex NOT NULL DEFAULT ''
);
CREATE INDEX index_AgMetadataSearchIndex_image ON AgMetadataSearchIndex( image );
CREATE TABLE Adobe_imageProperties (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    image INTEGER,
    propertiesString
);
CREATE INDEX index_Adobe_imageProperties_image ON Adobe_imageProperties( image );
CREATE TABLE Adobe_libraryImageDevelopSnapshot (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    digest,
    hasBigData INTEGER NOT NULL DEFAULT 0,
    hasDevelopAdjustments,
    image INTEGER,
    locked,
    name,
    snapshotID,
    text
);
CREATE INDEX index_Adobe_libraryImageDevelopSnapshot_image ON Adobe_libraryImageDevelopSnapshot( image );
CREATE TABLE Adobe_libraryImageDevelopHistoryStep (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    dateCreated,
    digest,
    hasBigData INTEGER NOT NULL DEFAULT 0,
    hasDevelopAdjustments,
    image INTEGER,
    name,
    relValueString,
    text,
    valueString
);
CREATE INDEX index_Adobe_libraryImageDevelopHistoryStep_imageDateCreated ON Adobe_libraryImageDevelopHistoryStep( image, dateCreated );
CREATE TABLE Adobe_libraryImageDevelop3DLUTColorTable (
    id_local INTEGER PRIMARY KEY,
    LUTFullString,
    LUTHash UNIQUE
);
CREATE TABLE Adobe_imageProofSettings (
    id_local INTEGER PRIMARY KEY,
    colorProfile,
    image INTEGER,
    renderingIntent
);
CREATE INDEX index_Adobe_imageProofSettings_image ON Adobe_imageProofSettings( image );
CREATE TABLE AgLibraryKeywordImage (
    id_local INTEGER PRIMARY KEY,
    image INTEGER NOT NULL DEFAULT 0,
    tag INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_AgLibraryKeywordImage_tag ON AgLibraryKeywordImage( tag );
CREATE INDEX index_AgLibraryKeywordImage_image ON AgLibraryKeywordImage( image );
CREATE TABLE Adobe_images (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    aspectRatioCache NOT NULL DEFAULT -1,
    bitDepth NOT NULL DEFAULT 0,
    captureTime,
    colorChannels NOT NULL DEFAULT 0,
    colorLabels NOT NULL DEFAULT '',
    colorMode NOT NULL DEFAULT -1,
    copyCreationTime NOT NULL DEFAULT -63113817600,
    copyName,
    copyReason,
    developSettingsIDCache,
    editLock INTEGER NOT NULL DEFAULT 0,
    fileFormat NOT NULL DEFAULT 'unset',
    fileHeight,
    fileWidth,
    hasMissingSidecars INTEGER,
    masterImage INTEGER,
    orientation,
    originalCaptureTime,
    originalRootEntity INTEGER,
    panningDistanceH,
    panningDistanceV,
    pick NOT NULL DEFAULT 0,
    positionInFolder NOT NULL DEFAULT 'z',
    propertiesCache,
    pyramidIDCache,
    rating,
    rootFile INTEGER NOT NULL DEFAULT 0,
    sidecarStatus,
    touchCount NOT NULL DEFAULT 0,
    touchTime NOT NULL DEFAULT 0
);
CREATE INDEX index_Adobe_images_rootFile ON Adobe_images( rootFile );
CREATE INDEX index_Adobe_images_ratingAndCaptureTime ON Adobe_images( rating, captureTime );
CREATE INDEX index_Adobe_images_originalRootEntity ON Adobe_images( originalRootEntity );
CREATE INDEX index_Adobe_images_masterImage ON Adobe_images( masterImage );
CREATE INDEX index_Adobe_images_captureTime ON Adobe_images( captureTime );
CREATE TABLE AgLibraryKeyword (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    dateCreated NOT NULL DEFAULT '',
    genealogy NOT NULL DEFAULT '',
    imageCountCache DEFAULT -1,
    includeOnExport INTEGER NOT NULL DEFAULT 1,
    includeParents INTEGER NOT NULL DEFAULT 1,
    includeSynonyms INTEGER NOT NULL DEFAULT 1,
    keywordType,
    lastApplied,
    lc_name,
    name,
    parent INTEGER
);
CREATE INDEX index_AgLibraryKeyword_genealogy ON AgLibraryKeyword( genealogy );
CREATE UNIQUE INDEX index_AgLibraryKeyword_parentAndLcName ON AgLibraryKeyword( parent, lc_name );
CREATE TABLE AgLibraryKeywordSynonym (
    id_local INTEGER PRIMARY KEY,
    keyword INTEGER NOT NULL DEFAULT 0,
    lc_name,
    name
);
CREATE INDEX index_AgLibraryKeywordSynonym_lc_name ON AgLibraryKeywordSynonym( lc_name );
CREATE INDEX index_AgLibraryKeywordSynonym_keyword ON AgLibraryKeywordSynonym( keyword );
CREATE TABLE AgDevelopAdditionalMetadata (
    id_local INTEGER PRIMARY KEY,
    caiAuthenticationInfo,
    hasCAISign INTEGER,
    hasDepthMap INTEGER,
    hasEnhance,
    image INTEGER
);
CREATE INDEX index_AgDevelopAdditionalMetadata_image ON AgDevelopAdditionalMetadata( image );
CREATE TABLE AgLibraryCollection (
    id_local INTEGER PRIMARY KEY,
    creationId NOT NULL DEFAULT '',
    genealogy NOT NULL DEFAULT '',
    imageCount,
    name NOT NULL DEFAULT '',
    parent INTEGER,
    systemOnly NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryCollection_parentAndName ON AgLibraryCollection( parent, name );
CREATE INDEX index_AgLibraryCollection_genealogy ON AgLibraryCollection( genealogy );
CREATE TABLE AgLibraryCollectionImage (
    id_local INTEGER PRIMARY KEY,
    collection INTEGER NOT NULL DEFAULT 0,
    image INTEGER NOT NULL DEFAULT 0,
    pick NOT NULL DEFAULT 0,
    positionInCollection
);
CREATE INDEX index_AgLibraryCollectionImage_collection ON AgLibraryCollectionImage( collection );
CREATE INDEX index_AgLibraryCollectionImage_imageCollection ON AgLibraryCollectionImage( image, collection );
CREATE TABLE AgLibraryCollectionContent (
    id_local INTEGER PRIMARY KEY,
    collection INTEGER NOT NULL DEFAULT 0,
    content,
    owningModule
);
CREATE INDEX index_AgLibraryCollectionContent_collection ON AgLibraryCollectionContent( collection );
CREATE INDEX index_AgLibraryCollectionContent_owningModule ON AgLibraryCollectionContent( owningModule );
CREATE TABLE AgLibraryCollectionStack (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    collapsed INTEGER NOT NULL DEFAULT 0,
    collection INTEGER NOT NULL DEFAULT 0,
    text NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryCollectionStack_stacksForCollection ON AgLibraryCollectionStack( collection, collapsed );
CREATE TABLE AgLibraryCollectionStackImage (
    id_local INTEGER PRIMARY KEY,
    collapsed INTEGER NOT NULL DEFAULT 0,
    collection INTEGER NOT NULL DEFAULT 0,
    image INTEGER NOT NULL DEFAULT 0,
    position NOT NULL DEFAULT '',
    stack INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_AgLibraryCollectionStackImage_stack ON AgLibraryCollectionStackImage( stack );
CREATE INDEX index_AgLibraryCollectionStackImage_orderByCollapseThenStackThenPosition ON AgLibraryCollectionStackImage( collection, collapsed, stack, position, image );
CREATE INDEX index_AgLibraryCollectionStackImage_orderByStackThenPosition ON AgLibraryCollectionStackImage( collection, stack, position, image, collapsed );
CREATE INDEX index_AgLibraryCollectionStackImage_image ON AgLibraryCollectionStackImage( image );
CREATE INDEX index_AgLibraryCollectionStackImage_getStackFromImage ON AgLibraryCollectionStackImage( collection, image, stack, position, collapsed );
CREATE INDEX index_AgLibraryCollectionStackImage_orderByPositionThenStack ON AgLibraryCollectionStackImage( collection, position, stack, image, collapsed );
CREATE TABLE AgLibraryCollectionLabel (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    collection INTEGER NOT NULL DEFAULT 0,
    label,
    labelData,
    labelGenerics,
    labelType NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryCollectionLabel_labelIndex ON AgLibraryCollectionLabel( label );
CREATE INDEX index_AgLibraryCollectionLabel_collectiondex ON AgLibraryCollectionLabel( collection );
CREATE UNIQUE INDEX index_AgLibraryCollectionLabel_collectionLabelIndex ON AgLibraryCollectionLabel( collection, label );
CREATE TABLE AgOutputImageAsset (
    id_local INTEGER PRIMARY KEY,
    assetId NOT NULL DEFAULT '',
    collection INTEGER NOT NULL DEFAULT 0,
    image INTEGER NOT NULL DEFAULT 0,
    moduleId NOT NULL DEFAULT ''
);
CREATE INDEX index_AgOutputImageAsset_image ON AgOutputImageAsset( image );
CREATE INDEX index_AgOutputImageAsset_findByCollectionGroupByImage ON AgOutputImageAsset( moduleId, collection, image, assetId );
CREATE INDEX index_AgOutputImageAsset_findByCollectionImage ON AgOutputImageAsset( collection, image, moduleId, assetId );
CREATE TABLE AgLibraryFolderStack (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    collapsed INTEGER NOT NULL DEFAULT 0,
    text NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryFolderStack_collapsed ON AgLibraryFolderStack( collapsed );
CREATE TABLE AgLibraryFolderStackImage (
    id_local INTEGER PRIMARY KEY,
    collapsed INTEGER NOT NULL DEFAULT 0,
    image INTEGER NOT NULL DEFAULT 0,
    position NOT NULL DEFAULT '',
    stack INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_AgLibraryFolderStackImage_orderByPositionThenStack ON AgLibraryFolderStackImage( position, stack, image, collapsed );
CREATE INDEX index_AgLibraryFolderStackImage_orderByStackThenPosition ON AgLibraryFolderStackImage( stack, position, image, collapsed );
CREATE INDEX index_AgLibraryFolderStackImage_getStackFromImage ON AgLibraryFolderStackImage( image, stack, position, collapsed );
CREATE INDEX index_AgLibraryFolderStackImage_orderByCollapseThenStackThenPosition ON AgLibraryFolderStackImage( collapsed, stack, position, image );
CREATE TABLE AgLibraryPublishedCollection (
    id_local INTEGER PRIMARY KEY,
    creationId NOT NULL DEFAULT '',
    genealogy NOT NULL DEFAULT '',
    imageCount,
    isDefaultCollection,
    name NOT NULL DEFAULT '',
    parent INTEGER,
    publishedUrl,
    remoteCollectionId,
    systemOnly NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryPublishedCollection_parentAndName ON AgLibraryPublishedCollection( parent, name );
CREATE INDEX index_AgLibraryPublishedCollection_genealogy ON AgLibraryPublishedCollection( genealogy );
CREATE TABLE AgLibraryPublishedCollectionImage (
    id_local INTEGER PRIMARY KEY,
    collection INTEGER NOT NULL DEFAULT 0,
    image INTEGER NOT NULL DEFAULT 0,
    pick NOT NULL DEFAULT 0,
    positionInCollection
);
CREATE INDEX index_AgLibraryPublishedCollectionImage_imageCollection ON AgLibraryPublishedCollectionImage( image, collection );
CREATE INDEX index_AgLibraryPublishedCollectionImage_collection ON AgLibraryPublishedCollectionImage( collection );
CREATE TABLE AgLibraryPublishedCollectionContent (
    id_local INTEGER PRIMARY KEY,
    collection INTEGER NOT NULL DEFAULT 0,
    content,
    owningModule
);
CREATE INDEX index_AgLibraryPublishedCollectionContent_collection ON AgLibraryPublishedCollectionContent( collection );
CREATE INDEX index_AgLibraryPublishedCollectionContent_owningModule ON AgLibraryPublishedCollectionContent( owningModule );
CREATE TABLE AgLibraryPublishedCollectionLabel (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    collection INTEGER NOT NULL DEFAULT 0,
    label,
    labelData,
    labelGenerics,
    labelType NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryPublishedCollectionLabel_collectiondex ON AgLibraryPublishedCollectionLabel( collection );
CREATE UNIQUE INDEX index_AgLibraryPublishedCollectionLabel_collectionLabelIndex ON AgLibraryPublishedCollectionLabel( collection, label );
CREATE INDEX index_AgLibraryPublishedCollectionLabel_labelIndex ON AgLibraryPublishedCollectionLabel( label );
CREATE TABLE AgLibraryIPTC (
    id_local INTEGER PRIMARY KEY,
    altTextAccessibility,
    caption,
    copyright,
    extDescrAccessibility,
    image INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_AgLibraryIPTC_image ON AgLibraryIPTC( image );
CREATE TABLE AgLibraryImport (
    id_local INTEGER PRIMARY KEY,
    imageCount,
    importDate NOT NULL DEFAULT '',
    name
);
CREATE TABLE AgLibraryImportImage (
    id_local INTEGER PRIMARY KEY,
    image INTEGER NOT NULL DEFAULT 0,
    import INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_AgLibraryImportImage_import ON AgLibraryImportImage( import );
CREATE UNIQUE INDEX index_AgLibraryImportImage_imageAndImport ON AgLibraryImportImage( image, import );
CREATE TABLE AgSpecialSourceContent (
    id_local INTEGER PRIMARY KEY,
    content,
    owningModule,
    source NOT NULL DEFAULT ''
);
CREATE UNIQUE INDEX index_AgSpecialSourceContent_sourceModule ON AgSpecialSourceContent( source, owningModule );
CREATE INDEX index_AgSpecialSourceContent_owningModule ON AgSpecialSourceContent( owningModule );
CREATE TABLE AgLibraryRootFolder (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    absolutePath UNIQUE NOT NULL DEFAULT '',
    name NOT NULL DEFAULT '',
    relativePathFromCatalog
);
CREATE TABLE AgLibraryFolder (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    parentId INTEGER,
    pathFromRoot NOT NULL DEFAULT '',
    rootFolder INTEGER NOT NULL DEFAULT 0,
    visibility INTEGER
);
CREATE UNIQUE INDEX index_AgLibraryFolder_rootFolderAndPath ON AgLibraryFolder( rootFolder, pathFromRoot );
CREATE INDEX index_AgLibraryFolder_parentId ON AgLibraryFolder( parentId );
CREATE TABLE AgLibraryFolderLabel (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    folder INTEGER NOT NULL DEFAULT 0,
    label,
    labelData,
    labelGenerics,
    labelType NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryFolderLabel_labelIndex ON AgLibraryFolderLabel( label );
CREATE INDEX index_AgLibraryFolderLabel_folderdex ON AgLibraryFolderLabel( folder );
CREATE UNIQUE INDEX index_AgLibraryFolderLabel_folderLabelIndex ON AgLibraryFolderLabel( folder, label );
CREATE TABLE AgLibraryFolderFavorite (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    favorite,
    folder INTEGER NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX index_AgLibraryFolderFavorite_folderFavoriteIndex ON AgLibraryFolderFavorite( folder, favorite );
CREATE INDEX index_AgLibraryFolderFavorite_favoriteIndex ON AgLibraryFolderFavorite( favorite );
CREATE INDEX index_AgLibraryFolderFavorite_folderIndex ON AgLibraryFolderFavorite( folder );
CREATE TABLE AgLibraryFile (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    baseName NOT NULL DEFAULT '',
    errorMessage,
    errorTime,
    extension NOT NULL DEFAULT '',
    externalModTime,
    folder INTEGER NOT NULL DEFAULT 0,
    idx_filename NOT NULL DEFAULT '',
    importHash,
    lc_idx_filename NOT NULL DEFAULT '',
    lc_idx_filenameExtension NOT NULL DEFAULT '',
    md5,
    modTime,
    originalFilename NOT NULL DEFAULT '',
    sidecarExtensions
);
CREATE UNIQUE INDEX index_AgLibraryFile_nameAndFolder ON AgLibraryFile( lc_idx_filename, folder );
CREATE INDEX index_AgLibraryFile_folder ON AgLibraryFile( folder );
CREATE INDEX index_AgLibraryFile_importHash ON AgLibraryFile( importHash );
CREATE TABLE AgLibraryImageAttributes (
    id_local INTEGER PRIMARY KEY,
    image INTEGER NOT NULL DEFAULT 0,
    lastExportTimestamp DEFAULT 0,
    lastPublishTimestamp DEFAULT 0
);
CREATE INDEX index_AgLibraryImageAttributes_image ON AgLibraryImageAttributes( image );
CREATE TABLE AgLibraryKeywordPopularity (
    id_local INTEGER PRIMARY KEY,
    occurrences NOT NULL DEFAULT 0,
    popularity NOT NULL DEFAULT 0,
    tag UNIQUE NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryKeywordPopularity_popularity ON AgLibraryKeywordPopularity( popularity );
CREATE TABLE AgLibraryKeywordCooccurrence (
    id_local INTEGER PRIMARY KEY,
    tag1 NOT NULL DEFAULT '',
    tag2 NOT NULL DEFAULT '',
    value NOT NULL DEFAULT 0
);
CREATE INDEX index_AgLibraryKeywordCooccurrence_tag1Search ON AgLibraryKeywordCooccurrence( tag1, value, tag2 );
CREATE INDEX index_AgLibraryKeywordCooccurrence_valueIndex ON AgLibraryKeywordCooccurrence( value );
CREATE INDEX index_AgLibraryKeywordCooccurrence_tagsLookup ON AgLibraryKeywordCooccurrence( tag1, tag2 );
CREATE TABLE AgPhotoComment (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    comment,
    commentRealname,
    commentUsername,
    dateCreated,
    photo INTEGER NOT NULL DEFAULT 0,
    remoteId NOT NULL DEFAULT '',
    remotePhoto INTEGER,
    url
);
CREATE INDEX index_AgPhotoComment_remotePhoto ON AgPhotoComment( remotePhoto );
CREATE INDEX index_AgPhotoComment_photo ON AgPhotoComment( photo );
CREATE INDEX index_AgPhotoComment_remoteId ON AgPhotoComment( remoteId );
CREATE TABLE AgPhotoProperty (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    dataType,
    internalValue,
    photo INTEGER NOT NULL DEFAULT 0,
    propertySpec INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_AgPhotoProperty_propertySpec ON AgPhotoProperty( propertySpec );
CREATE UNIQUE INDEX index_AgPhotoProperty_pluginKey ON AgPhotoProperty( photo, propertySpec );
CREATE TABLE AgPhotoPropertyArrayElement (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    arrayIndex NOT NULL DEFAULT '',
    dataType,
    internalValue,
    photo INTEGER NOT NULL DEFAULT 0,
    propertySpec INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_AgPhotoPropertyArrayElement_propertySpec ON AgPhotoPropertyArrayElement( propertySpec );
CREATE UNIQUE INDEX index_AgPhotoPropertyArrayElement_pluginKey ON AgPhotoPropertyArrayElement( photo, propertySpec, arrayIndex );
CREATE TABLE AgSearchablePhotoProperty (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    dataType,
    internalValue,
    lc_idx_internalValue,
    photo INTEGER NOT NULL DEFAULT 0,
    propertySpec INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_AgSearchablePhotoProperty_propertyValue_lc ON AgSearchablePhotoProperty( propertySpec, lc_idx_internalValue );
CREATE INDEX index_AgSearchablePhotoProperty_lc_idx_internalValue ON AgSearchablePhotoProperty( lc_idx_internalValue );
CREATE UNIQUE INDEX index_AgSearchablePhotoProperty_pluginKey ON AgSearchablePhotoProperty( photo, propertySpec );
CREATE INDEX index_AgSearchablePhotoProperty_propertyValue ON AgSearchablePhotoProperty( propertySpec, internalValue );
CREATE TABLE AgSearchablePhotoPropertyArrayElement (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    arrayIndex NOT NULL DEFAULT '',
    dataType,
    internalValue,
    lc_idx_internalValue,
    photo INTEGER NOT NULL DEFAULT 0,
    propertySpec INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_AgSearchablePhotoPropertyArrayElement_propertyValue ON AgSearchablePhotoPropertyArrayElement( propertySpec, internalValue );
CREATE UNIQUE INDEX index_AgSearchablePhotoPropertyArrayElement_pluginKey ON AgSearchablePhotoPropertyArrayElement( photo, propertySpec, arrayIndex );
CREATE INDEX index_AgSearchablePhotoPropertyArrayElement_lc_idx_internalValue ON AgSearchablePhotoPropertyArrayElement( lc_idx_internalValue );
CREATE INDEX index_AgSearchablePhotoPropertyArrayElement_propertyValue_lc ON AgSearchablePhotoPropertyArrayElement( propertySpec, lc_idx_internalValue );
CREATE TABLE AgPhotoPropertySpec (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    flattenedAttributes,
    key NOT NULL DEFAULT '',
    pluginVersion NOT NULL DEFAULT '',
    sourcePlugin NOT NULL DEFAULT '',
    userVisibleName
);
CREATE UNIQUE INDEX index_AgPhotoPropertySpec_pluginKey ON AgPhotoPropertySpec( sourcePlugin, key, pluginVersion );
CREATE TABLE AgRemotePhoto (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    collection INTEGER NOT NULL DEFAULT 0,
    commentCount,
    developSettingsDigest,
    fileContentsHash,
    fileModTimestamp,
    metadataDigest,
    mostRecentCommentTime,
    orientation,
    photo INTEGER NOT NULL DEFAULT 0,
    photoNeedsUpdating DEFAULT 2,
    publishCount,
    remoteId,
    serviceAggregateRating,
    url
);
CREATE INDEX index_AgRemotePhoto_collectionNeedsUpdating ON AgRemotePhoto( collection, photoNeedsUpdating );
CREATE UNIQUE INDEX index_AgRemotePhoto_collectionRemoteId ON AgRemotePhoto( collection, remoteId );
CREATE INDEX index_AgRemotePhoto_photo ON AgRemotePhoto( photo );
CREATE UNIQUE INDEX index_AgRemotePhoto_collectionPhoto ON AgRemotePhoto( collection, photo );
CREATE TABLE AgVideoInfo (
    id_local INTEGER PRIMARY KEY,
    duration,
    frame_rate,
    has_audio INTEGER NOT NULL DEFAULT 1,
    has_video INTEGER NOT NULL DEFAULT 1,
    image INTEGER NOT NULL DEFAULT 0,
    poster_frame NOT NULL DEFAULT '0000000000000000/0000000000000001',
    poster_frame_set_by_user INTEGER NOT NULL DEFAULT 0,
    trim_end NOT NULL DEFAULT '0000000000000000/0000000000000001',
    trim_start NOT NULL DEFAULT '0000000000000000/0000000000000001'
);
CREATE INDEX index_AgVideoInfo_image ON AgVideoInfo( image );
CREATE TABLE AgLibraryFace (
    id_local INTEGER PRIMARY KEY,
    bl_x,
    bl_y,
    br_x,
    br_y,
    cluster INTEGER,
    compatibleVersion,
    ignored INTEGER,
    image INTEGER NOT NULL DEFAULT 0,
    imageOrientation NOT NULL DEFAULT '',
    orientation,
    origination NOT NULL DEFAULT 0,
    propertiesCache,
    regionType NOT NULL DEFAULT 0,
    skipSuggestion INTEGER,
    tl_x NOT NULL DEFAULT '',
    tl_y NOT NULL DEFAULT '',
    touchCount NOT NULL DEFAULT 0,
    touchTime NOT NULL DEFAULT -63113817600,
    tr_x,
    tr_y,
    version
);
CREATE INDEX index_AgLibraryFace_cluster ON AgLibraryFace( cluster );
CREATE INDEX index_AgLibraryFace_image ON AgLibraryFace( image );
CREATE TABLE Adobe_faceProperties (
    id_local INTEGER PRIMARY KEY,
    face INTEGER,
    propertiesString
);
CREATE INDEX index_Adobe_faceProperties_face ON Adobe_faceProperties( face );
CREATE TABLE AgLibraryFaceData (
    id_local INTEGER PRIMARY KEY,
    data,
    face INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_AgLibraryFaceData_face ON AgLibraryFaceData( face );
CREATE TABLE AgLibraryFaceCluster (
    id_local INTEGER PRIMARY KEY,
    keyFace INTEGER
);
CREATE INDEX index_AgLibraryFaceCluster_keyFace ON AgLibraryFaceCluster( keyFace );
CREATE TABLE AgLibraryKeywordFace (
    id_local INTEGER PRIMARY KEY,
    face INTEGER NOT NULL DEFAULT 0,
    keyFace INTEGER,
    rankOrder,
    tag INTEGER NOT NULL DEFAULT 0,
    userPick INTEGER,
    userReject INTEGER
);
CREATE INDEX index_AgLibraryKeywordFace_face ON AgLibraryKeywordFace( face );
CREATE INDEX index_AgLibraryKeywordFace_tag ON AgLibraryKeywordFace( tag );
CREATE TABLE Adobe_libraryImageFaceProcessHistory (
    id_local INTEGER PRIMARY KEY,
    image INTEGER NOT NULL DEFAULT 0,
    lastFaceDetector,
    lastFaceRecognizer,
    lastImageIndexer,
    lastImageOrientation,
    lastTryStatus,
    userTouched
);
CREATE INDEX index_Adobe_libraryImageFaceProcessHistory_image ON Adobe_libraryImageFaceProcessHistory( image );
CREATE TABLE AgLibraryImageSearchData (
    id_local INTEGER PRIMARY KEY,
    featInfo,
    height,
    idDesc,
    idDescCh,
    image INTEGER NOT NULL DEFAULT 0,
    width
);
CREATE INDEX index_AgLibraryImageSearchData_image ON AgLibraryImageSearchData( image );
CREATE TABLE AgSourceColorProfileConstants (
    id_local INTEGER PRIMARY KEY,
    image INTEGER NOT NULL DEFAULT 0,
    profileName NOT NULL DEFAULT 'Untagged'
);
CREATE INDEX index_AgSourceColorProfileConstants_image ON AgSourceColorProfileConstants( image );
CREATE INDEX index_AgSourceColorProfileConstants_imageSourceColorProfileName ON AgSourceColorProfileConstants( profileName, image );
CREATE TABLE AgDNGProxyInfo (
    id_local INTEGER PRIMARY KEY,
    fileUUID NOT NULL DEFAULT '',
    status NOT NULL DEFAULT 'U',
    statusDateTime NOT NULL DEFAULT 0
);
CREATE INDEX index_AgDNGProxyInfo_statusDateTimeForUUID ON AgDNGProxyInfo( status, statusDateTime, fileUUID );
CREATE INDEX index_AgDNGProxyInfo_uuidStatusDateTime ON AgDNGProxyInfo( fileUUID, status, statusDateTime );
CREATE TABLE AgLibraryOzFeedbackInfo (
    id_local INTEGER PRIMARY KEY,
    image NOT NULL DEFAULT '',
    lastFeedbackTime,
    lastReadTime,
    newCommentCount NOT NULL DEFAULT 0,
    newFavoriteCount NOT NULL DEFAULT 0,
    ozAssetId NOT NULL DEFAULT '',
    ozCatalogId NOT NULL DEFAULT '',
    ozSpaceId NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryOzFeedbackInfo_lastFeedbackTime ON AgLibraryOzFeedbackInfo( lastFeedbackTime );
CREATE UNIQUE INDEX index_AgLibraryOzFeedbackInfo_assetAndSpaceAndCatalog ON AgLibraryOzFeedbackInfo( ozAssetId, ozSpaceId, ozCatalogId );
CREATE TABLE Adobe_imageDevelopBeforeSettings (
    id_local INTEGER PRIMARY KEY,
    beforeDigest,
    beforeHasDevelopAdjustments,
    beforePresetID,
    beforeText,
    developSettings INTEGER,
    hasBigData INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX index_Adobe_imageDevelopBeforeSettings_developSettings ON Adobe_imageDevelopBeforeSettings( developSettings );
CREATE TABLE Adobe_imageDevelopSettings (
    id_local INTEGER PRIMARY KEY,
    allowFastRender INTEGER,
    beforeSettingsIDCache,
    croppedHeight,
    croppedWidth,
    digest,
    fileHeight,
    fileWidth,
    filterHeight,
    filterWidth,
    grayscale INTEGER,
    hasAIMasks INTEGER NOT NULL DEFAULT 0,
    hasBigData INTEGER NOT NULL DEFAULT 0,
    hasDevelopAdjustments INTEGER,
    hasDevelopAdjustmentsEx,
    hasLensBlur INTEGER NOT NULL DEFAULT 0,
    hasMasks INTEGER NOT NULL DEFAULT 0,
    hasPointColor INTEGER NOT NULL DEFAULT 0,
    hasRetouch,
    hasSettings1,
    hasSettings2,
    historySettingsID,
    image INTEGER,
    isHdrEditMode INTEGER NOT NULL DEFAULT 0,
    processVersion,
    profileCorrections,
    removeChromaticAberration,
    settingsID,
    snapshotID,
    text,
    validatedForVersion,
    whiteBalance
);
CREATE INDEX index_Adobe_imageDevelopSettings_image ON Adobe_imageDevelopSettings( image );
CREATE INDEX index_Adobe_imageDevelopSettings_digest ON Adobe_imageDevelopSettings( digest );
CREATE TABLE Adobe_namedIdentityPlate (
    id_local INTEGER PRIMARY KEY,
    id_global UNIQUE NOT NULL,
    description,
    identityPlate,
    identityPlateHash,
    moduleFont,
    moduleSelectedTextColor,
    moduleTextColor
);
CREATE INDEX index_Adobe_namedIdentityPlate_description ON Adobe_namedIdentityPlate( description );
CREATE INDEX index_Adobe_namedIdentityPlate_identityPlateHash ON Adobe_namedIdentityPlate( identityPlateHash );
CREATE TABLE AgMRULists (
    id_local INTEGER PRIMARY KEY,
    listID NOT NULL DEFAULT '',
    timestamp NOT NULL DEFAULT 0,
    value NOT NULL DEFAULT ''
);
CREATE INDEX index_AgMRULists_listID ON AgMRULists( listID );
CREATE TABLE AgHarvestedExifMetadata (
    id_local INTEGER PRIMARY KEY,
    image INTEGER,
    aperture,
    cameraModelRef INTEGER,
    cameraSNRef INTEGER,
    dateDay,
    dateMonth,
    dateYear,
    flashFired INTEGER,
    focalLength,
    gpsLatitude,
    gpsLongitude,
    gpsSequence NOT NULL DEFAULT 0,
    hasGPS INTEGER,
    isoSpeedRating,
    lensRef INTEGER,
    shutterSpeed
);
CREATE INDEX index_AgHarvestedExifMetadata_cameraSNRef ON AgHarvestedExifMetadata( cameraSNRef );
CREATE INDEX index_AgHarvestedExifMetadata_lensRef ON AgHarvestedExifMetadata( lensRef );
CREATE INDEX index_AgHarvestedExifMetadata_focalLength ON AgHarvestedExifMetadata( focalLength );
CREATE INDEX index_AgHarvestedExifMetadata_flashFired ON AgHarvestedExifMetadata( flashFired );
CREATE INDEX index_AgHarvestedExifMetadata_shutterSpeed ON AgHarvestedExifMetadata( shutterSpeed );
CREATE INDEX index_AgHarvestedExifMetadata_cameraModelRef ON AgHarvestedExifMetadata( cameraModelRef );
CREATE INDEX index_AgHarvestedExifMetadata_isoSpeedRating ON AgHarvestedExifMetadata( isoSpeedRating );
CREATE INDEX index_AgHarvestedExifMetadata_image ON AgHarvestedExifMetadata( image );
CREATE INDEX index_AgHarvestedExifMetadata_date ON AgHarvestedExifMetadata( dateYear, dateMonth, dateDay, image );
CREATE INDEX index_AgHarvestedExifMetadata_gpsCluster ON AgHarvestedExifMetadata( hasGPS, gpsLatitude, gpsLongitude, image );
CREATE INDEX index_AgHarvestedExifMetadata_aperture ON AgHarvestedExifMetadata( aperture );
CREATE TABLE AgHarvestedIptcMetadata (
    id_local INTEGER PRIMARY KEY,
    image INTEGER,
    cityRef INTEGER,
    copyrightState INTEGER,
    countryRef INTEGER,
    creatorRef INTEGER,
    isoCountryCodeRef INTEGER,
    jobIdentifierRef INTEGER,
    locationDataOrigination NOT NULL DEFAULT 'unset',
    locationGPSSequence NOT NULL DEFAULT -1,
    locationRef INTEGER,
    stateRef INTEGER
);
CREATE INDEX index_AgHarvestedIptcMetadata_isoCountryCodeRef ON AgHarvestedIptcMetadata( isoCountryCodeRef );
CREATE INDEX index_AgHarvestedIptcMetadata_stateRef ON AgHarvestedIptcMetadata( stateRef );
CREATE INDEX index_AgHarvestedIptcMetadata_locationDataOrigination ON AgHarvestedIptcMetadata( locationDataOrigination );
CREATE INDEX index_AgHarvestedIptcMetadata_image ON AgHarvestedIptcMetadata( image );
CREATE INDEX index_AgHarvestedIptcMetadata_jobIdentifierRef ON AgHarvestedIptcMetadata( jobIdentifierRef );
CREATE INDEX index_AgHarvestedIptcMetadata_cityRef ON AgHarvestedIptcMetadata( cityRef );
CREATE INDEX index_AgHarvestedIptcMetadata_creatorRef ON AgHarvestedIptcMetadata( creatorRef );
CREATE INDEX index_AgHarvestedIptcMetadata_countryRef ON AgHarvestedIptcMetadata( countryRef );
CREATE INDEX index_AgHarvestedIptcMetadata_copyrightState ON AgHarvestedIptcMetadata( copyrightState );
CREATE INDEX index_AgHarvestedIptcMetadata_locationRef ON AgHarvestedIptcMetadata( locationRef );
CREATE TABLE AgHarvestedDNGMetadata (
    id_local INTEGER PRIMARY KEY,
    image INTEGER,
    hasFastLoadData INTEGER,
    hasLossyCompression INTEGER,
    isDNG INTEGER,
    isHDR INTEGER,
    isPano INTEGER,
    isReducedResolution INTEGER
);
CREATE INDEX index_AgHarvestedDNGMetadata_byHasLossyCompression ON AgHarvestedDNGMetadata( hasLossyCompression, image, isDNG, hasFastLoadData, isReducedResolution, isPano, isHDR );
CREATE INDEX index_AgHarvestedDNGMetadata_byIsHDR ON AgHarvestedDNGMetadata( isHDR, image, isDNG, hasFastLoadData, hasLossyCompression, isReducedResolution, isPano );
CREATE INDEX index_AgHarvestedDNGMetadata_byIsPano ON AgHarvestedDNGMetadata( isPano, image, isDNG, hasFastLoadData, hasLossyCompression, isReducedResolution, isHDR );
CREATE INDEX index_AgHarvestedDNGMetadata_byHasFastLoadData ON AgHarvestedDNGMetadata( hasFastLoadData, image, isDNG, hasLossyCompression, isReducedResolution, isPano, isHDR );
CREATE INDEX index_AgHarvestedDNGMetadata_byImage ON AgHarvestedDNGMetadata( image, isDNG, hasFastLoadData, hasLossyCompression, isReducedResolution, isPano, isHDR );
CREATE INDEX index_AgHarvestedDNGMetadata_byIsDNG ON AgHarvestedDNGMetadata( isDNG, image, hasFastLoadData, hasLossyCompression, isReducedResolution, isPano, isHDR );
CREATE INDEX index_AgHarvestedDNGMetadata_byIsReducedResolution ON AgHarvestedDNGMetadata( isReducedResolution, image, isDNG, hasFastLoadData, hasLossyCompression, isPano, isHDR );
CREATE TABLE AgInternedIptcCreator (
    id_local INTEGER PRIMARY KEY,
    searchIndex,
    value
);
CREATE INDEX index_AgInternedIptcCreator_value ON AgInternedIptcCreator( value );
CREATE INDEX index_AgInternedIptcCreator_searchIndex ON AgInternedIptcCreator( searchIndex );
CREATE TABLE AgInternedIptcCountry (
    id_local INTEGER PRIMARY KEY,
    searchIndex,
    value
);
CREATE INDEX index_AgInternedIptcCountry_value ON AgInternedIptcCountry( value );
CREATE INDEX index_AgInternedIptcCountry_searchIndex ON AgInternedIptcCountry( searchIndex );
CREATE TABLE AgInternedIptcLocation (
    id_local INTEGER PRIMARY KEY,
    searchIndex,
    value
);
CREATE INDEX index_AgInternedIptcLocation_value ON AgInternedIptcLocation( value );
CREATE INDEX index_AgInternedIptcLocation_searchIndex ON AgInternedIptcLocation( searchIndex );
CREATE TABLE AgInternedIptcState (
    id_local INTEGER PRIMARY KEY,
    searchIndex,
    value
);
CREATE INDEX index_AgInternedIptcState_searchIndex ON AgInternedIptcState( searchIndex );
CREATE INDEX index_AgInternedIptcState_value ON AgInternedIptcState( value );
CREATE TABLE AgInternedExifCameraModel (
    id_local INTEGER PRIMARY KEY,
    searchIndex,
    value
);
CREATE INDEX index_AgInternedExifCameraModel_value ON AgInternedExifCameraModel( value );
CREATE INDEX index_AgInternedExifCameraModel_searchIndex ON AgInternedExifCameraModel( searchIndex );
CREATE TABLE AgInternedExifCameraSN (
    id_local INTEGER PRIMARY KEY,
    searchIndex,
    value
);
CREATE INDEX index_AgInternedExifCameraSN_value ON AgInternedExifCameraSN( value );
CREATE INDEX index_AgInternedExifCameraSN_searchIndex ON AgInternedExifCameraSN( searchIndex );
CREATE TABLE AgInternedIptcJobIdentifier (
    id_local INTEGER PRIMARY KEY,
    searchIndex,
    value
);
CREATE INDEX index_AgInternedIptcJobIdentifier_value ON AgInternedIptcJobIdentifier( value );
CREATE INDEX index_AgInternedIptcJobIdentifier_searchIndex ON AgInternedIptcJobIdentifier( searchIndex );
CREATE TABLE AgInternedIptcIsoCountryCode (
    id_local INTEGER PRIMARY KEY,
    searchIndex,
    value
);
CREATE INDEX index_AgInternedIptcIsoCountryCode_value ON AgInternedIptcIsoCountryCode( value );
CREATE INDEX index_AgInternedIptcIsoCountryCode_searchIndex ON AgInternedIptcIsoCountryCode( searchIndex );
CREATE TABLE AgInternedIptcCity (
    id_local INTEGER PRIMARY KEY,
    searchIndex,
    value
);
CREATE INDEX index_AgInternedIptcCity_searchIndex ON AgInternedIptcCity( searchIndex );
CREATE INDEX index_AgInternedIptcCity_value ON AgInternedIptcCity( value );
CREATE TABLE AgInternedExifLens (
    id_local INTEGER PRIMARY KEY,
    searchIndex,
    value
);
CREATE INDEX index_AgInternedExifLens_searchIndex ON AgInternedExifLens( searchIndex );
CREATE INDEX index_AgInternedExifLens_value ON AgInternedExifLens( value );
CREATE TABLE AgHarvestedMetadataWorklist (
    id_local INTEGER PRIMARY KEY,
    taskID UNIQUE NOT NULL DEFAULT '',
    taskStatus NOT NULL DEFAULT 'pending',
    whenPosted NOT NULL DEFAULT ''
);
CREATE INDEX index_AgHarvestedMetadataWorklist_taskIDCluster ON AgHarvestedMetadataWorklist( taskID, whenPosted, taskStatus );
CREATE INDEX index_AgHarvestedMetadataWorklist_statusCluster ON AgHarvestedMetadataWorklist( taskStatus, whenPosted, taskID );
CREATE TABLE AgLibraryImageXMPUpdater (
    id_local INTEGER PRIMARY KEY,
    taskID UNIQUE NOT NULL DEFAULT '',
    taskStatus NOT NULL DEFAULT 'pending',
    whenPosted NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryImageXMPUpdater_statusCluster ON AgLibraryImageXMPUpdater( taskStatus, whenPosted, taskID );
CREATE INDEX index_AgLibraryImageXMPUpdater_taskIDCluster ON AgLibraryImageXMPUpdater( taskID, whenPosted, taskStatus );
CREATE TABLE AgLibraryImageSaveXMP (
    id_local INTEGER PRIMARY KEY,
    taskID UNIQUE NOT NULL DEFAULT '',
    taskStatus NOT NULL DEFAULT 'pending',
    whenPosted NOT NULL DEFAULT ''
);
CREATE INDEX index_AgLibraryImageSaveXMP_taskIDCluster ON AgLibraryImageSaveXMP( taskID, whenPosted, taskStatus );
CREATE INDEX index_AgLibraryImageSaveXMP_statusCluster ON AgLibraryImageSaveXMP( taskStatus, whenPosted, taskID );
CREATE TABLE AgPublishListenerWorklist (
    id_local INTEGER PRIMARY KEY,
    taskID UNIQUE NOT NULL DEFAULT '',
    taskStatus NOT NULL DEFAULT 'pending',
    whenPosted NOT NULL DEFAULT ''
);
CREATE INDEX index_AgPublishListenerWorklist_statusCluster ON AgPublishListenerWorklist( taskStatus, whenPosted, taskID );
CREATE INDEX index_AgPublishListenerWorklist_taskIDCluster ON AgPublishListenerWorklist( taskID, whenPosted, taskStatus );
CREATE TABLE AgDNGProxyInfoUpdater (
    id_local INTEGER PRIMARY KEY,
    taskID UNIQUE NOT NULL DEFAULT '',
    taskStatus NOT NULL DEFAULT 'pending',
    whenPosted NOT NULL DEFAULT ''
);
CREATE INDEX index_AgDNGProxyInfoUpdater_taskIDCluster ON AgDNGProxyInfoUpdater( taskID, whenPosted, taskStatus );
CREATE INDEX index_AgDNGProxyInfoUpdater_statusCluster ON AgDNGProxyInfoUpdater( taskStatus, whenPosted, taskID );
CREATE TABLE AgTempImages ( image INTEGER PRIMARY KEY );
CREATE TABLE AgLibraryUpdatedImages ( image INTEGER PRIMARY KEY );
CREATE TABLE AgLastCatalogExport ( image INTEGER PRIMARY KEY );
CREATE TABLE AgLibraryCollectionStackData(
    stack INTEGER,
    collection INTEGER NOT NULL DEFAULT 0,
    stackCount INTEGER NOT NULL DEFAULT 0,
    stackParent INTEGER
);
CREATE INDEX index_AgLibraryCollectionStackData ON AgLibraryCollectionStackData( stack, collection, stackCount, stackParent );
CREATE TRIGGER AgLibraryCollectionStackData_initStackData
	AFTER INSERT ON AgLibraryCollectionStackData
	FOR EACH ROW
	BEGIN
		UPDATE AgLibraryCollectionStackData
			SET stackCount = (
				SELECT COUNT( * ) FROM AgLibraryCollectionStackImage
				WHERE stack = NEW.stack AND collection = NEW.collection )
			WHERE stack = NEW.stack AND collection = NEW.collection;
		UPDATE AgLibraryCollectionStackData
			SET stackParent = (
				SELECT image FROM AgLibraryCollectionStackImage
				WHERE stack = NEW.stack AND collection = NEW.collection AND
				      position = 1 )
			WHERE stack = NEW.stack AND collection = NEW.collection;
	END;
CREATE TABLE AgLibraryFolderStackData (
    stack INTEGER,
    stackCount INTEGER NOT NULL DEFAULT 0,
    stackParent INTEGER
);
CREATE INDEX index_AgLibraryFolderStackData ON AgLibraryFolderStackData( stack, stackCount, stackParent );
CREATE TRIGGER AgLibraryFolderStackData_initStackData
	AFTER INSERT ON AgLibraryFolderStackData
	FOR EACH ROW
	BEGIN
		UPDATE AgLibraryFolderStackData
			SET stackCount = (
				SELECT COUNT( * ) FROM AgLibraryFolderStackImage
				WHERE stack = NEW.stack )
			WHERE stack = NEW.stack;
		UPDATE AgLibraryFolderStackData
			SET stackParent = (
				SELECT image FROM AgLibraryFolderStackImage
				WHERE stack = NEW.stack AND position = 1 )
			WHERE stack = NEW.stack;

	END;
CREATE TABLE LrMobileSyncChangeCounter(
	id PRIMARY KEY,
	changeCounter NOT NULL
);
CREATE TABLE AgLibraryCollectionTrackedAssets (
	collection NOT NULL,
	ozCatalogId DEFAULT "current"
);
CREATE TABLE AgLibraryImageChangeCounter(
	image PRIMARY KEY,
	changeCounter DEFAULT 0,
	lastSyncedChangeCounter DEFAULT 0,
	changedAtTime DEFAULT '',
	localTimeOffsetSecs DEFAULT 0
);
CREATE TABLE AgLibraryImageOzAssetIds(
	id_local NOT NULL DEFAULT 0,
	image NOT NULL,
	ozCatalogId NOT NULL,
	ozAssetId DEFAULT "pending",
	ownedByCatalog DEFAULT 'Y'
);
CREATE TABLE AgDeletedOzAssetIds(
	id_local NOT NULL DEFAULT 0,
	ozCatalogId NOT NULL,
	ozAssetId NOT NULL,
	changeCounter DEFAULT 0,
	lastSyncedChangeCounter DEFAULT 0
);
CREATE TABLE AgLibraryImageSyncedAssetData (
	image NOT NULL,
	payloadKey NOT NULL,
	payloadData NOT NULL
);
CREATE TABLE AgPendingOzAssetBinaryDownloads(
	ozAssetId NOT NULL,
	ozCatalogId NOT NULL,
	whenQueued NOT NULL,
	path NOT NULL,
	state DEFAULT "master"
);
CREATE TABLE AgPendingOzAssets(
	ozAssetId NOT NULL,
	ozCatalogId NOT NULL,
	state DEFAULT "needs_binary",
	path NOT NULL,
	payload NOT NULL
);
CREATE TABLE AgPendingOzDocs(
	id_local INTEGER NOT NULL,
	ozDocId PRIMARY KEY,
	ozCatalogId NOT NULL,
	state DEFAULT "needs_binary",
	fileName NOT NULL,
	path NOT NULL,
	binaryType DEFAULT "original",
	needAux DEFAULT 0,
	needDevelopXmp DEFAULT 0,
	needSidecar DEFAULT 0,
	payload NOT NULL,
	revId DEFAULT 0,
	isLibImage DEFAULT 0,
	isPathChanged DEFAULT 0,
	errorDescription Default ''
);
CREATE TABLE AgPendingOzUploads(
	id_local INTEGER NOT NULL,
	localId,
	ozDocId,
	operation NOT NULL,
	ozCatalogId NOT NULL,
	changeCounter DEFAULT 0
);
CREATE TABLE AgUnsupportedOzAssets(
	id_local INTEGER PRIMARY KEY,
	ozAssetId NOT NULL,
	ozCatalogId NOT NULL,
	path NOT NULL,
	type NOT NULL,
	payload NOT NULL
);
CREATE TABLE AgOzAssetSettings(
	id_local INTEGER NOT NULL,
	image PRIMARY KEY,
	ozCatalogId NOT NULL,
	sha256 NOT NULL,
	updatedTime NOT NULL
);
CREATE TABLE AgOzDocRevIds(
	localId NOT NULL,
	currRevId NOT NULL,
	docType NOT NULL,
	PRIMARY KEY (localId, docType)
);
CREATE TABLE AgPendingOzAssetDevelopSettings(
	ozAssetId NOT NULL,
	ozCatalogId NOT NULL,
	payloadHash NOT NULL,
	developUserUpdated
);
CREATE TABLE AgPendingOzAuxBinaryDownloads(
	auxId NOT NULL,
	ozAssetId NOT NULL,
	ozCatalogId NOT NULL,
	payloadHash NOT NULL,
	whenQueued NOT NULL,
	state NOT NULL
);
CREATE TABLE AgLibraryCollectionChangeCounter(
	collection PRIMARY KEY,
	changeCounter DEFAULT 0,
	lastSyncedChangeCounter DEFAULT 0
);
CREATE TABLE AgLibraryCollectionOzAlbumIds(
	id_local NOT NULL DEFAULT 0,
	collection NOT NULL,
	ozCatalogId NOT NULL,
	ozAlbumId DEFAULT "pending"
);
CREATE TABLE AgDeletedOzAlbumIds(
	id_local NOT NULL DEFAULT 0,
	ozCatalogId NOT NULL,
	ozAlbumId NOT NULL,
	changeCounter DEFAULT 0,
	lastSyncedChangeCounter DEFAULT 0
);
CREATE TABLE AgLibraryCollectionSyncedAlbumData(
	collection NOT NULL,
	payloadKey NOT NULL,
	payloadData NOT NULL
);
CREATE TABLE AgLibraryCollectionCoverImage(
	id_local NOT NULL DEFAULT 0,
	collection PRIMARY KEY,
	collectionImage NOT NULL
);
CREATE TABLE AgLibraryCollectionImageChangeCounter(
	collectionImage PRIMARY KEY,
	collection NOT NULL,
	image NOT NULL,
	changeCounter DEFAULT 0,
	lastSyncedChangeCounter DEFAULT 0
);
CREATE TABLE AgLibraryCollectionImageOzAlbumAssetIds(
	id_local NOT NULL DEFAULT 0,
	collectionImage NOT NULL,
	collection NOT NULL,
	image NOT NULL,
	ozCatalogId NOT NULL,
	ozAlbumAssetId DEFAULT "pending"
);
CREATE TABLE AgLibraryCollectionImageOzSortOrder(
	collectionImage  PRIMARY KEY,
	collection NOT NULL,
	positionInCollection NOT NULL,
	ozSortOrder NOT NULL
);
CREATE TABLE AgDeletedOzAlbumAssetIds(
	id_local NOT NULL DEFAULT 0,
	ozCatalogId NOT NULL,
	ozAlbumAssetId NOT NULL,
	changeCounter DEFAULT 0,
	lastSyncedChangeCounter DEFAULT 0
);
CREATE TABLE AgPendingOzAlbumAssetIds(
	ozCatalogId NOT NULL,
	ozAlbumAssetId NOT NULL,
	ozAssetId NOT NULL,
	ozAlbumId NOT NULL,
	ozSortOrder DEFAULT "",
	ozIsCover DEFAULT 0
);
CREATE TABLE AgOzSpaceIds(
	ozCatalogId NOT NULL,
	ozSpaceId NOT NULL
);
CREATE TABLE AgDeletedOzSpaceIds(
	id_local NOT NULL DEFAULT 0,
	ozCatalogId NOT NULL,
	ozSpaceId NOT NULL,
	changeCounter default 0,
	lastSyncedChangeCounter DEFAULT 0
);
CREATE TABLE AgOzSpaceAlbumIds( 
	id_local NOT NULL DEFAULT 0,
	ozCatalogId NOT NULL,
	ozAlbumId NOT NULL,
	ozSpaceId NOT NULL,
	ozSpaceAlbumId NOT NULL
);
CREATE TABLE AgLibraryOzCommentIds(
	ozCatalogId NOT NULL,
	ozSpaceId NOT NULL,
	ozAssetId NOT NULL,
	ozCommentId NOT NULL,
	timestamp NOT NULL
);
CREATE TABLE AgLibraryOzFavoriteIds(
	ozCatalogId NOT NULL,
	ozSpaceId NOT NULL,
	ozAssetId NOT NULL,
	ozFavoriteId NOT NULL,
	timestamp NOT NULL
);
CREATE TABLE AgLibraryFileAssetMetadata(
	fileId PRIMARY KEY,
	sha256 NOT NULL,
	fileSize DEFAULT 0
);
CREATE TABLE AgOzAuxBinaryMetadata(
	auxId NOT NULL,
	ozAssetId NOT NULL,
	ozCatalogId NOT NULL,
	digest NOT NULL,
	sha256 NOT NULL,
	fileSize DEFAULT 0,
	type NOT NULL
);
CREATE TABLE AgOzCorruptedAuxIds(
	auxId NOT NULL,
	ozAssetId NOT NULL,
	ozCatalogId NOT NULL
);
CREATE UNIQUE INDEX index_AgLibraryCollectionTrackedAssets_primaryKey ON
	AgLibraryCollectionTrackedAssets( collection, ozCatalogId );
CREATE INDEX index_AgLibraryCollectionTrackedAssets_byOzCatalogId ON
	AgLibraryCollectionTrackedAssets( ozCatalogId, collection );
CREATE INDEX index_AgLibraryImageChangeCounter_changeCounter ON
	AgLibraryImageChangeCounter( changeCounter, image );
CREATE UNIQUE INDEX index_AgLibraryImageSyncedAssetData_primaryKey ON
	AgLibraryImageSyncedAssetData( image, payloadKey );
CREATE UNIQUE INDEX index_AgLibraryImageOzAssetIds_primaryKey ON
	AgLibraryImageOzAssetIds( image, ozCatalogId );
CREATE INDEX index_AgLibraryImageOzAssetIds_imageFromAssetIdLookup ON
	AgLibraryImageOzAssetIds( id_local, ozAssetId, ozCatalogId, image, ownedByCatalog );
CREATE UNIQUE INDEX index_AgDeletedOzAssetIds_primaryKey ON
	AgDeletedOzAssetIds( ozCatalogId, ozAssetId );
CREATE INDEX index_AgDeletedOzAssetIds_changeCounter ON
	AgDeletedOzAssetIds( changeCounter, ozCatalogId, ozAssetId );
CREATE UNIQUE INDEX index_AgPendingOzAssets_primaryKey ON
	AgPendingOzAssets( ozAssetId, ozCatalogId );
CREATE INDEX index_AgPendingOzAssets_stateSearches ON
	AgPendingOzAssets( state, ozCatalogId, ozAssetId );
CREATE UNIQUE INDEX index_AgPendingOzAssetBinaryDownloads_primaryKey ON
	AgPendingOzAssetBinaryDownloads( ozAssetId, ozCatalogId );
CREATE INDEX index_AgPendingOzAssetBinaryDownloads_catalogIdOrdering ON
	AgPendingOzAssetBinaryDownloads( ozCatalogId, whenQueued, state, ozAssetId, path );
CREATE INDEX index_AgPendingOzAssetBinaryDownloads_stateSearches ON
	AgPendingOzAssetBinaryDownloads( state, ozCatalogId, whenQueued, ozAssetId );
CREATE INDEX index_AgLibraryCollectionChangeCounter_changeCounter ON
	AgLibraryCollectionChangeCounter( changeCounter, collection );
CREATE UNIQUE INDEX index_AgLibraryCollectionOzAlbumIds_primaryKey ON
	AgLibraryCollectionOzAlbumIds( collection, ozCatalogId );
CREATE INDEX index_AgLibraryCollectionOzAlbumIds_collectionFromAlbumIdLookup ON
	AgLibraryCollectionOzAlbumIds( ozAlbumId, ozCatalogId, collection );
CREATE INDEX index_AgLibraryCollectionOzAlbumIds_catalogAlbumsLookup ON
	AgLibraryCollectionOzAlbumIds( ozCatalogId, ozAlbumId, collection );
CREATE UNIQUE INDEX index_AgDeletedOzAlbumIds_primaryKey ON
	AgDeletedOzAlbumIds( ozCatalogId, ozAlbumId );
CREATE INDEX index_AgDeletedOzAlbumIds_changeCounter ON
	AgDeletedOzAlbumIds( changeCounter, ozCatalogId, ozAlbumId );
CREATE UNIQUE INDEX index_AgLibraryCollectionSyncedAlbumData_primaryKey ON
	AgLibraryCollectionSyncedAlbumData( collection, payloadKey );
CREATE INDEX index_AgLibraryCollectionImageChangeCounter_changeCounter ON
	AgLibraryCollectionImageChangeCounter( changeCounter, collectionImage,
											collection, image );
CREATE UNIQUE INDEX index_AgLibraryCollectionImageOzAlbumAssetIds_primaryKey ON
	AgLibraryCollectionImageOzAlbumAssetIds( collectionImage, ozCatalogId,
												collection, image );
CREATE INDEX index_AgLibraryCollectionImageOzAlbumAssetIds_collectionFromAlbumAssetIdLookup ON
	AgLibraryCollectionImageOzAlbumAssetIds( ozAlbumAssetId, ozCatalogId,
												collectionImage, collection,
												image );
CREATE INDEX index_AgLibraryCollectionImageOzAlbumAssetIds_collectionAlbumAssetsLookup ON
	AgLibraryCollectionImageOzAlbumAssetIds( collection, ozCatalogId );
CREATE INDEX index_AgLibraryCollectionImageOzAlbumAssetIds_imageAlbumAssetsLookup ON
	AgLibraryCollectionImageOzAlbumAssetIds( image, ozCatalogId );
CREATE UNIQUE INDEX index_AgDeletedOzAlbumAssetIds_primaryKey ON
	AgDeletedOzAlbumAssetIds( ozCatalogId, ozAlbumAssetId );
CREATE INDEX index_AgDeletedOzAlbumAssetIds_changeCounter ON
	AgDeletedOzAlbumAssetIds( changeCounter, ozCatalogId, ozAlbumAssetId );
CREATE UNIQUE INDEX index_AgPendingOzAlbumAssetIds_primaryKey ON
	AgPendingOzAlbumAssetIds( ozCatalogId, ozAlbumAssetId, ozAssetId, ozAlbumId );
CREATE INDEX index_AgPendingOzAlbumAssetIds_byAlbumAssetId ON
	AgPendingOzAlbumAssetIds( ozAlbumAssetId, ozAssetId, ozCatalogId, ozAlbumId );
CREATE INDEX index_AgPendingOzAlbumAssetIds_byAssetId ON
	AgPendingOzAlbumAssetIds( ozAssetId, ozCatalogId, ozAlbumAssetId, ozAlbumId );
CREATE INDEX index_AgPendingOzAlbumAssetIds_byAlbumId ON
	AgPendingOzAlbumAssetIds( ozAlbumId, ozCatalogId, ozAlbumAssetId, ozAssetId );
CREATE UNIQUE INDEX index_AgOzSpaceAlbumIds_primaryKey ON
	AgOzSpaceAlbumIds( ozSpaceAlbumId );
CREATE INDEX index_AgOzSpaceAlbumIds_bySpaceId ON
	AgOzSpaceAlbumIds( ozSpaceId, ozCatalogId );
CREATE INDEX index_AgOzSpaceAlbumIds_byAlbumId ON
	AgOzSpaceAlbumIds( ozAlbumId, ozCatalogId );
CREATE UNIQUE INDEX index_AgOzSpaceIds_primaryKey ON
	AgOzSpaceIds( ozCatalogId, ozSpaceId );
CREATE UNIQUE INDEX index_AgDeletedOzSpaceIds_primaryKey ON
	AgDeletedOzSpaceIds( ozCatalogId, ozSpaceId );
CREATE UNIQUE INDEX index_AgLibraryOzCommentIds_primaryKey ON
	AgLibraryOzCommentIds( ozCatalogId, ozCommentId );
CREATE INDEX index_AgLibraryOzCommentIds_byAsset ON
	AgLibraryOzCommentIds( ozCatalogId, ozSpaceId, ozAssetId );
CREATE INDEX index_AgLibraryOzCommentIds_bySpace ON 
	AgLibraryOzCommentIds( ozCatalogId, ozSpaceId );
CREATE UNIQUE INDEX index_AgLibraryOzFavoriteIds_primaryKey ON
	AgLibraryOzFavoriteIds( ozCatalogId, ozFavoriteId );
CREATE INDEX index_AgLibraryOzFavoriteIds_byAsset ON
	AgLibraryOzFavoriteIds( ozCatalogId, ozSpaceId, ozAssetId );
CREATE INDEX index_AgLibraryOzFavoriteIds_bySpace ON 
	AgLibraryOzFavoriteIds( ozCatalogId, ozSpaceId );
CREATE INDEX index_AgLibraryFileAssetMetadata_sha256ToFileId  ON
	AgLibraryFileAssetMetadata( sha256, fileSize );
CREATE INDEX index_AgOzAuxBinaryMetadata_byAsset  ON
	AgOzAuxBinaryMetadata( ozAssetId );
CREATE INDEX index_AgOzCorruptedAuxIds_byAsset  ON
	AgOzCorruptedAuxIds( ozAssetId );
CREATE TABLE MigrationSchemaVersion(
			version TEXT PRIMARY KEY
		);
CREATE TABLE MigratedImages(
			ozAssetId NOT NULL,
			ozCatalogId NOT NULL,
			localId INTEGER NOT NULL,
			UNIQUE ( localId, ozCatalogId )
		);
CREATE TABLE MigratedCollections(
			ozAlbumId NOT NULL,
			ozCatalogId NOT NULL,
			ozName NOT NULL,
			localId INTEGER NOT NULL,
			UNIQUE ( localId, ozCatalogId )
		);
CREATE TABLE MigratedCollectionImages(
			ozAlbumId NOT NULL,
			ozAlbumAssetId NOT NULL,
			ozCatalogId NOT NULL,
			localCollectionId INTEGER NOT NULL,
			localCollectionImageId INTEGER NOT NULL,
			UNIQUE ( localCollectionImageId, ozCatalogId )
		);
CREATE TABLE MigratedInfo(
			ozCatalogId TEXT PRIMARY KEY,
			migrationStatus NOT NULL,
			timestamp NOT NULL
		);
CREATE TRIGGER AgLibraryCollectionStack_propagateCollapseState
								   AFTER UPDATE OF collapsed ON AgLibraryCollectionStack
								   FOR EACH ROW
								   BEGIN
										UPDATE AgLibraryCollectionStackImage
										SET collapsed = NEW.collapsed
										WHERE AgLibraryCollectionStackImage.stack = NEW.id_local;
									END;
CREATE TRIGGER AgLibraryCollectionStackData_delete
								AFTER DELETE ON AgLibraryCollectionStack
								FOR EACH ROW
								BEGIN
									DELETE FROM AgLibraryCollectionStackData WHERE stack = OLD.id_local AND collection = OLD.collection;
								END;
CREATE TRIGGER AgLibraryCollectionStackData_init
								AFTER INSERT ON AgLibraryCollectionStack
								FOR EACH ROW
								BEGIN
									INSERT INTO AgLibraryCollectionStackData( stack, collection ) VALUES( NEW.id_local, NEW.collection );
								END;
CREATE TRIGGER AgLibraryCollectionStackImage_propagateStackParentOnAdd
								   AFTER INSERT ON AgLibraryCollectionStackImage
								   FOR EACH ROW WHEN NEW.position = 1
								   BEGIN
										UPDATE AgLibraryCollectionStackData
										SET stackParent = NEW.image
										WHERE stack = NEW.stack AND
										      collection = NEW.collection;
									END;
CREATE TRIGGER AgLibraryCollectionStackImage_propagateStackParentOnUpdate
								   AFTER UPDATE OF position ON AgLibraryCollectionStackImage
								   FOR EACH ROW WHEN NEW.position = 1
								   BEGIN
										UPDATE AgLibraryCollectionStackData
										SET stackParent = NEW.image
										WHERE stack = NEW.stack AND
										      collection = NEW.collection;
									END;
CREATE TRIGGER AgLibraryCollectionStackImage_updateCountOnDelete
								   AFTER DELETE ON AgLibraryCollectionStackImage
								   FOR EACH ROW
								   BEGIN
										UPDATE AgLibraryCollectionStackData
										SET stackCount = MAX( 0, stackCount - 1 )
										WHERE stack = OLD.stack AND
										      collection = OLD.collection;
									END;
CREATE TRIGGER AgLibraryCollectionStackImage_updateCountOnAdd
								   AFTER INSERT ON AgLibraryCollectionStackImage
								   FOR EACH ROW
								   BEGIN
										UPDATE AgLibraryCollectionStackData
										SET stackCount = stackCount + 1
										WHERE stack = NEW.stack AND
										      collection = NEW.collection;
									END;
CREATE TRIGGER AgLibraryFolderStack_propagateCollapseState
								   AFTER UPDATE OF collapsed ON AgLibraryFolderStack
								   FOR EACH ROW
								   BEGIN
										UPDATE AgLibraryFolderStackImage
										SET collapsed = NEW.collapsed
										WHERE AgLibraryFolderStackImage.stack = NEW.id_local;
									END;
CREATE TRIGGER AgLibraryFolderStackData_delete
								AFTER DELETE ON AgLibraryFolderStack
								FOR EACH ROW
								BEGIN
									DELETE FROM AgLibraryFolderStackData WHERE stack = OLD.id_local;
								END;
CREATE TRIGGER AgLibraryFolderStackData_init
								AFTER INSERT ON AgLibraryFolderStack
								FOR EACH ROW
								BEGIN
									INSERT INTO AgLibraryFolderStackData( stack ) VALUES( NEW.id_local );
								END;
CREATE TRIGGER AgLibraryFolderStackImage_propagateStackParentOnAdd
								   AFTER INSERT ON AgLibraryFolderStackImage
								   FOR EACH ROW WHEN NEW.position = 1
								   BEGIN
										UPDATE AgLibraryFolderStackData
										SET stackParent = NEW.image
										WHERE stack = NEW.stack;
									END;
CREATE TRIGGER AgLibraryFolderStackImage_propagateStackParentOnUpdate
								   AFTER UPDATE OF position ON AgLibraryFolderStackImage
								   FOR EACH ROW WHEN NEW.position = 1
								   BEGIN
										UPDATE AgLibraryFolderStackData
										SET stackParent = NEW.image
										WHERE stack = NEW.stack;
									END;
CREATE TRIGGER AgLibraryFolderStackImage_updateStackCountOnDelete
								   AFTER DELETE ON AgLibraryFolderStackImage
								   FOR EACH ROW
								   BEGIN
										UPDATE AgLibraryFolderStackData
										SET stackCount = MAX( 0, stackCount - 1 )
										WHERE stack = OLD.stack;
									END;
CREATE TRIGGER AgLibraryFolderStackImage_updateCountOnAdd
								   AFTER INSERT ON AgLibraryFolderStackImage
								   FOR EACH ROW
								   BEGIN
										UPDATE AgLibraryFolderStackData
										SET stackCount = stackCount + 1
										WHERE stack = NEW.stack;
									END;
CREATE TRIGGER trigger_AgDNGProxyInfo_fileDeleted
											AFTER DELETE ON AgLibraryFile
											FOR EACH ROW
											BEGIN
												UPDATE AgDNGProxyInfo
												SET status = 'D', statusDateTime = datetime( 'now' )
												WHERE fileUUID = OLD.id_global;
											END;
CREATE TRIGGER trigger_AgDNGProxyInfo_fileInserted
						   					 AFTER INSERT ON AgLibraryFile
											 FOR EACH ROW
											 BEGIN
												UPDATE AgDNGProxyInfo
												SET status = 'U', statusDateTime = datetime( 'now' )
												WHERE fileUUID = NEW.id_global;
											END;
CREATE TRIGGER trigger_AgLibraryCollectionCoverImage_delete_collection
	AFTER DELETE on AgLibraryCollection
	FOR EACH ROW
	BEGIN
		DELETE FROM AgLibraryCollectionCoverImage
		WHERE collection = OLD.id_local;
	END;
CREATE TRIGGER trigger_AgLibraryCollectionCoverImage_delete_collectionImage
	AFTER DELETE on AgLibraryCollectionImage
	FOR EACH ROW
	BEGIN
		DELETE FROM AgLibraryCollectionCoverImage
		WHERE collection = OLD.collection AND collectionImage = OLD.id_local;
	END;
CREATE TABLE sqlite_stat1(tbl,idx,stat);
CREATE TABLE sqlite_stat4(tbl,idx,neq,nlt,ndlt,sample);
