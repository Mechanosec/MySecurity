# GraphQL Types — joyreactor.cc

Отримано через introspection. Тільки читання схеми — жодних запитів до даних.

---

## Object Types

### `Award`

- `id`: `ID!`
- `name`: `String!`
- `description`: `String!`
- `nextAward`: `Award`
- `picUrl`: `String!`

### `AwardUser`

- `award`: `Award!`
- `user`: `User!`
- `hidden`: `Boolean!`

### `BanLog`

- `post`: `Post`
- `comment`: `Comment`
- `reasonCode`: `Int!`
- `reasonText`: `String`
- `days`: `Int!`
- `unban`: `Boolean!`
- `flags`: `Int!`
- `createdAt`: `DateTimeTz!`
- `tag`: `Tag`

### `Comment`

- `id`: `ID!`
- `text`: `String!`
- `attributes`: `[?!]!`
- `contentEditedAt`: `DateTimeTz`
- `contentUpdatedAt`: `DateTimeTz`
- `contentVersion`: `Int!`
- `createdAt`: `DateTimeTz!`
- `parent`: `Content`
- `post`: `Post`
- `rating`: `Float!`
- `level`: `Int!`
- `user`: `User!`
- `vote`: `CommentVote`
- `voted`: `Boolean`
- `banned`: `Boolean!`
- `locale`: `String!`

### `CommentAttributeEmbed`

- `id`: `ID!`
- `comment`: `Comment!`
- `type`: `AttributeType!`
- `insertId`: `Int`
- `value`: `String!`
- `image`: `Image!`

### `CommentAttributePicture`

- `id`: `ID!`
- `comment`: `Comment!`
- `type`: `AttributeType!`
- `insertId`: `Int`
- `image`: `Image!`

### `CommentMutationResult`

- `comment`: `Comment`
- `errorCode`: `Int!`
- `query`: `Query!`

### `CommentPager`

- `id`: `ID!`
- `comments`: `[?!]!`
- `count`: `Int!`

### `CommentTop`

- `week`: `[?!]!`
- `two_days`: `[?!]!`

### `CommentVote`

- `createdAt`: `DateTimeTz!`
- `power`: `Float!`
- `comment`: `Comment!`
- `user`: `User!`

### `ConfirmMutationResult`

- `user`: `User`
- `query`: `Query!`

### `Contact`

- `counterpart`: `User!`
- `unread`: `Boolean!`

### `Domain`

- `tag`: `Tag!`
- `name`: `String!`
- `id`: `ID!`

### `Image`

- `width`: `Int!`
- `height`: `Int!`
- `comment`: `String`
- `type`: `ImageType!`
- `hasVideo`: `Boolean!`
- `id`: `ID!`

### `Mutation`

- `login`: `Query!`
- `refreshLogin`: `MutationResult!`
- `logout`: `Query!`
- `register`: `RegisterMutationResult!`
- `confirmEmail`: `ConfirmMutationResult!`
- `resetPassword`: `ResetMutationResult!`
- `resetPasswordRequest`: `MutationResult!`
- `setPhone`: `MutationResult!`
- `comment`: `CommentMutationResult!`
- `post`: `PostMutationResult!`
- `edit`: `Query!`
- `delete`: `MutationResult!`
- `favorite`: `Query!`
- `favoriteTag`: `Query!`
- `friend`: `Query!`
- `vote`: `Query!`
- `pollVote`: `Query!`
- `addTagExtended`: `MutationResult!`
- `removeTag`: `Query!`
- `temporaryImage`: `TemporaryImageMutationResult!`
- `ban`: `MutationResult!`
- `unban`: `MutationResult!`
- `changeLocale`: `MutationResult!`
- `reportAbuse`: `MutationResult!`
- `reportDupe`: `MutationResult!`
- `proclaimDupe`: `MutationResult!`
- `userSettings`: `MutationResult!`
- `privateMessage`: `MutationResult`
- `giftPremium`: `MutationResult!`
- `bindBoosty`: `MutationResult!`
- `bindTags`: `MutationResult!`
- `addTagRelation`: `MutationResult!`
- `removeTagRelation`: `MutationResult!`
- `tagSettings`: `MutationResult!`

### `MutationResult`

- `success`: `Boolean!`
- `message`: `String`
- `query`: `Query!`

### `NewPostCounts`

- `discussionPersonal`: `Int!`

### `Phone`

- `status`: `PhoneStatus!`
- `code`: `String`

### `Poll`

- `question`: `String!`
- `answers`: `[?!]!`
- `voted`: `Boolean!`

### `PollAnswer`

- `id`: `ID!`
- `answer`: `String!`
- `count`: `Int!`

### `Post`

- `id`: `ID!`
- `text`: `String!`
- `attributes`: `[?!]!`
- `contentEditedAt`: `DateTimeTz`
- `contentUpdatedAt`: `DateTimeTz`
- `contentVersion`: `Int!`
- `commentsCount`: `Int!`
- `viewedCommentsCount`: `Int!`
- `viewedCommentsAt`: `DateTimeTz`
- `bestComments`: `[?!]!`
- `comments`: `[?!]!`
- `nsfw`: `Boolean!`
- `unsafe`: `Boolean!`
- `banned`: `Boolean!`
- `createdAt`: `DateTimeTz!`
- `rating`: `Float!`
- `ratingGeneral`: `Float!`
- `locales`: `[?!]!`
- `user`: `User!`
- `postTags`: `[?!]!`
- `vote`: `PostVote`
- `favorite`: `Boolean!`
- `minusThreshold`: `Float!`
- `header`: `String`
- `seoAttributes`: `PostSeoAttributes!`
- `poll`: `Poll`
- `editableUntil`: `DateTimeTz`

### `PostAttributeEmbed`

- `id`: `ID!`
- `post`: `Post`
- `type`: `AttributeType!`
- `insertId`: `Int`
- `value`: `String!`
- `image`: `Image!`

### `PostAttributePicture`

- `id`: `ID!`
- `post`: `Post`
- `type`: `AttributeType!`
- `insertId`: `Int`
- `image`: `Image!`

### `PostMutationResult`

- `post`: `Post`
- `query`: `Query!`

### `PostPager`

- `id`: `ID!`
- `posts`: `[?!]!`
- `count`: `Int!`

### `PostSeoAttributes`

- `title`: `String!`
- `description`: `String!`
- `ocr`: `String`
- `similarPosts`: `[?!]!`

### `PostTag`

- `tag`: `Tag!`
- `deletable`: `Boolean!`

### `PostVote`

- `createdAt`: `DateTimeTz!`
- `gold`: `Boolean!`
- `power`: `Float!`
- `post`: `Post!`
- `user`: `User!`

### `PrivateMessage`

- `message`: `String!`
- `direction`: `PrivateMessageDirection!`
- `createdAt`: `DateTimeTz!`
- `unread`: `Boolean!`

### `Query`

- `tagAutocomplete`: `[?!]!`
- `me`: `User`
- `user`: `User`
- `tag`: `Tag`
- `weekTopPosts`: `[?!]!`
- `yearTopPosts`: `[?!]!`
- `changedPosts`: `[?!]!`
- `search`: `SearchResult!`
- `initialTags`: `[?!]!`
- `checkEmail`: `Boolean!`
- `searchHistory`: `SearchHistory!`
- `node`: `Node`
- `donated`: `Int!`
- `trends`: `[?!]!`
- `tagTopBySubscribers`: `TagTopBySubscribers!`
- `commentTop`: `CommentTop!`
- `fandomePromo`: `[?!]!`

### `RateLimitInfo`

- `remainingWeight`: `Int!`
- `weight`: `Int!`
- `queryCount`: `Int!`
- `cacheHitCount`: `Int!`
- `cacheMissCount`: `Int!`
- `cacheBatchCount`: `Int!`

### `RegisterMutationResult`

- `user`: `User`
- `query`: `Query!`

### `ResetMutationResult`

- `user`: `User`
- `query`: `Query!`

### `SearchHistory`

- `searchQueries`: `[?!]!`
- `count`: `Int!`

### `SearchResult`

- `postPager`: `PostPager`
- `tags`: `[Tag!]`
- `similarQueries`: `[String!]`
- `excluded`: `Boolean!`

### `Tag`

- `id`: `ID!`
- `articlePost`: `Post`
- `articleImage`: `Image`
- `bigImage`: `Image`
- `category`: `Tag`
- `count`: `Int!`
- `updatedAt`: `String!`
- `image`: `Image`
- `mainTag`: `Tag!`
- `name`: `String!`
- `seoName`: `String!`
- `synonyms`: `String`
- `nsfw`: `Boolean!`
- `rating`: `Float!`
- `subscribers`: `Int!`
- `unsafe`: `Boolean!`
- `showAsCategory`: `Boolean!`
- `postPager`: `PostPager!`
- `tagPager`: `TagPager!`
- `userTag`: `UserTag`
- `childTags`: `[Tag!]`
- `subTagsMenu`: `[Tag!]`
- `subTags`: `[Tag!]`
- `hierarchy`: `[?!]!`
- `moderators`: `[?!]!`

### `TagCloud`

- `tag`: `Tag!`
- `count`: `Int!`

### `TagPager`

- `id`: `ID!`
- `tags`: `[?!]!`
- `count`: `Int!`

### `TagTopBySubscribers`

- `all`: `[?!]!`
- `week`: `[?!]!`
- `two_days`: `[?!]!`

### `TemporaryImageMutationResult`

- `hash`: `String!`
- `query`: `Query!`

### `User`

- `active`: `Boolean!`
- `about`: `String`
- `bestPostNum`: `Int!`
- `createdAt`: `Date!`
- `goodPostNum`: `Int!`
- `lastVisit`: `Date!`
- `lastLogin`: `DateTimeTz`
- `postPager`: `PostPager!`
- `commentPager`: `CommentPager!`
- `topTagRatings`: `[UserTag!]`
- `postNum`: `Int!`
- `commentNum`: `Int!`
- `sequentialVisits`: `Int!`
- `totalVisits`: `Int!`
- `ratingWeek`: `Float!`
- `rating`: `Float!`
- `username`: `String!`
- `urls`: `[?!]!`
- `userState`: `UserState`
- `hasNewPrivateMessage`: `Boolean!`
- `contacts`: `[?!]!`
- `privateMessages`: `[?!]!`
- `hideSubscriptionsRatings`: `Boolean!`
- `gifByClick`: `Boolean!`
- `settings`: `UserSettings!`
- `goldStatus`: `Boolean!`
- `goldStatusExpire`: `DateTimeTz`
- `platinumStatus`: `Boolean!`
- `platinumStatusExpire`: `DateTimeTz`
- `token`: `String!`
- `favoritePostPager`: `PostPager!`
- `favoriteTagCloud`: `[?!]!`
- `friendPostPager`: `PostPager!`
- `personalDiscussionPostPager`: `PostPager!`
- `flags`: `Int!`
- `blockedTags`: `[?!]!`
- `subscribedTags`: `[?!]!`
- `moderatedTags`: `[?!]!`
- `tagBans`: `[?!]!`
- `blockedUsers`: `[?!]!`
- `friends`: `[?!]!`
- `banLogs`: `[?!]!`
- `postsBannedUntil`: `DateTimeTz`
- `commentsBannedUntil`: `DateTimeTz`
- `phone`: `Phone!`
- `newPostCounts`: `NewPostCounts!`
- `awards`: `[?!]!`
- `canSendPrivateMessage`: `Boolean!`
- `donatedLeft`: `Int!`
- `id`: `ID!`

### `UserSettings`

- `email`: `String!`
- `fullName`: `String!`
- `about`: `String!`
- `privateMessagePolicy`: `PrivateMessagePolicy!`
- `commentsToMail`: `Boolean!`
- `postsToMail`: `Boolean!`
- `privateToMail`: `Boolean!`
- `hideSubscriptions`: `Boolean!`
- `hideSpoilers`: `Boolean!`
- `gifByClick`: `Boolean!`
- `removeGifVideo`: `Boolean!`
- `showGoldNick`: `Boolean!`
- `goldStatusExtend`: `Boolean!`
- `image`: `Image`

### `UserTag`

- `tag`: `Tag!`
- `rating`: `Float!`
- `state`: `UserTagState!`
- `user`: `User!`
- `bannedUntil`: `DateTimeTz`

---

## Input Types

### `OrderByClause`

- `column`: `String!`
- `order`: `SortOrder!`

### `PollInput`

- `question`: `String!`
- `answers`: `[?!]!`

### `TagSettingsInput`

- `articlePost`: `ID`
- `synonyms`: `String`
- `showThreshold`: `Float`
- `nsfw`: `Boolean`
- `trend`: `Boolean`

### `UserSettingsInput`

- `fullName`: `String`
- `about`: `String`
- `privateMessagePolicy`: `PrivateMessagePolicy`
- `commentsToMail`: `Boolean`
- `postsToMail`: `Boolean`
- `privateToMail`: `Boolean`
- `hideSubscriptions`: `Boolean`
- `hideSpoilers`: `Boolean`
- `gifByClick`: `Boolean`
- `removeGifVideo`: `Boolean`
- `showGoldNick`: `Boolean`
- `goldStatusExtend`: `Boolean`
- `urls`: `[String!]`

---

## Enums

### `AttributeType`

- `PICTURE`
- `YOUTUBE`
- `VIMEO`
- `COUB`
- `SOUNDCLOUD`
- `BANDCAMP`

### `ImageType`

- `PNG`
- `JPEG`
- `GIF`
- `BMP`
- `TIFF`
- `MP4`
- `WEBM`
- `WEBP`

### `OrderByRelationAggregateFunction`

- `COUNT`

### `OrderByRelationWithColumnAggregateFunction`

- `AVG`
- `MIN`
- `MAX`
- `SUM`
- `COUNT`

### `PhoneStatus`

- `NOT_ENTERED`
- `AWAITING_SMS`
- `PHONE_NUMBER_MISMATCH`
- `ACTIVE`

### `PostLineType`

- `ALL`
- `NEW`
- `GOOD`
- `BEST`
- `DISCUSSION_ALL`
- `DISCUSSION_FLAME`
- `DISCUSSION_GOOD`

### `PrivateMessageDirection`

- `INCOMING`
- `OUTGOING`

### `PrivateMessagePolicy`

- `ALL`
- `ONE_STAR`
- `FRIENDS`

### `SortOrder`

- `ASC`
- `DESC`

### `TagLineType`

- `NEW`
- `BEST`

### `TagRelationType`

- `CATEGORY`
- `PARENT`

### `Trashed`

- `ONLY`
- `WITH`
- `WITHOUT`

### `UserPremiumType`

- `GOLD`
- `PLATINUM`

### `UserState`

- `NEUTRAL`
- `FRIEND`
- `BLOCKED`

### `UserTagState`

- `SUBSCRIBED`
- `UNSUBSCRIBED`
- `BLOCKED`
- `MODERATED`

### `VoteType`

- `MINUS`
- `PLUS`
- `PLUS_GOLD`
